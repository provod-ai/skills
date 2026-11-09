"""Offline profile/evidence joins for the existing SEO master. No collectors or effects.

A valid import is not SEO acceptance. Native actors supply actual observations;
this module verifies identity, coverage and provenance before projecting them.
"""
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile
from urllib.parse import urlsplit


PROFILE_FIELDS = ('schema_version site_id origins source_selectors allowed_targets publisher '
                  'templates locale_market_facts capability_facts action_scope input_locators '
                  'account_property_locators coverage_policy issue_refs memory_locator '
                  'source_config_binding').split()
CHECK_FIELDS = ('id revision semantic_key title category capability_ids mechanism_ids aliases kind '
                'applies_if inputs method acceptance severity evidence_requirement upstream_source_ids '
                'source_provenance expiry fix_readback limits').split()
ARTIFACT_FIELDS = ('id path sha256 observed_at collector collector_version target '
                   'source_config_binding coverage limitations').split()
OBSERVATION_FIELDS = ('check_id check_revision scope target applicability execution verdict '
                      'artifact_ids reason actor window readback').split()
CLASSES = ('machine', 'expert', 'account', 'longitudinal')
APPLICABILITY = ('applicable', 'not-applicable', 'undetermined')
EXECUTION = ('not-run', 'completed', 'blocked', 'error')
VERDICT = ('pass', 'fail', 'unknown')
FRESHNESS = ('current', 'dated', 'stale', 'binding-mismatch', 'unverified')
HASH = re.compile(r'^[0-9a-f]{64}$')
SITE_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def object_fields(value, fields, label):
    require(isinstance(value, dict), label + ' must be an object')
    require(all(field in value for field in fields), label + ' missing fields: ' + ', '.join(field for field in fields if field not in value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(path):
    path = Path(os.path.abspath(path))
    require(not any(part.is_symlink() for part in (path, *path.parents)), 'symlink path is not allowed: ' + str(path))
    return path


def regular(path):
    path = safe(path)
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), 'not a regular file: ' + str(path))
    return path


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def finite(value):
    result = float(value)
    require(math.isfinite(result), 'nonfinite JSON number')
    return result


def bad_constant(value):
    raise ValueError('non-JSON numeric constant: ' + value)


def parse_json(data):
    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                      parse_float=finite, parse_constant=bad_constant)


def load(path):
    return parse_json(regular(path).read_bytes())


def dump(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=True, allow_nan=False)
        handle.write('\n')


def when(value):
    require(text(value), 'timestamp must be a nonempty ISO8601 string')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('invalid ISO8601 timestamp: ' + value) from None
    require(result.tzinfo is not None, 'timestamp requires an explicit timezone: ' + value)
    return result.astimezone(timezone.utc)


def strings(value, label, nonempty=False):
    require(isinstance(value, list) and all(text(item) for item in value), label + ' must be a string array')
    require(not nonempty or bool(value), label + ' must not be empty')
    require(len(value) == len(set(value)), label + ' contains duplicates')


def validate_binding(binding, site_id):
    object_fields(binding, ['site_id', 'source', 'config_sha256', 'serving'], 'source_config_binding')
    require(binding['site_id'] == site_id, 'profile binding site_id differs from profile')
    object_fields(binding['source'], ['kind', 'revision'], 'binding source')
    require(text(binding['source']['kind']), 'source kind is required')
    require(binding['source']['kind'] in ('commit', 'tree', 'blob', 'files', 'unclassified', 'unknown'), 'source kind must retain commit/tree/blob/files/unclassified/unknown typing')
    require(binding['source']['revision'] is None or text(binding['source']['revision']), 'source revision must be null or a string')
    value = binding['config_sha256']
    require(value is None or isinstance(value, str) and HASH.fullmatch(value), 'config_sha256 must be null or SHA256')
    object_fields(binding['serving'], ['origin', 'revision'], 'binding serving')
    require(binding['serving']['origin'] is None or text(binding['serving']['origin']), 'serving origin must be null or a string')
    require(binding['serving']['revision'] is None or text(binding['serving']['revision']), 'serving revision must be null or a string')
    if 'account_properties' in binding:
        require(isinstance(binding['account_properties'], dict), 'account_properties must be an object')
    if 'files_sha256' in binding['source']:
        values = binding['source']['files_sha256']
        require(isinstance(values, dict) and all(text(k) and isinstance(v, str) and HASH.fullmatch(v) for k, v in values.items()), 'source files_sha256 must map paths to SHA256')


def bound_file(descriptor, base, inputs, label, with_bytes=False):
    object_fields(descriptor, ['path', 'sha256'], label)
    require(text(descriptor['path']) and isinstance(descriptor['sha256'], str)
            and HASH.fullmatch(descriptor['sha256']), label + ' requires path and SHA256')
    path = Path(descriptor['path'])
    path = regular(path if path.is_absolute() else Path(base) / path)
    data = path.read_bytes()
    require(bool(data) and hashlib.sha256(data).hexdigest() == descriptor['sha256'], label + ' is empty or SHA256 differs')
    inputs.append({'path': str(path), 'sha256': descriptor['sha256']})
    return (path, data) if with_bytes else path


def member_set(value, inline, manifest, base, inputs):
    require((inline in value) != (manifest in value), 'membership requires exactly one inline list or manifest')
    if inline in value:
        members = value[inline]
    else:
        descriptor = value[manifest]
        object_fields(descriptor, ['path', 'sha256', 'format', 'member_field'], 'membership manifest')
        require(text(descriptor['member_field']), 'membership member_field is required')
        path, data = bound_file(descriptor, base, inputs, 'membership manifest', with_bytes=True)
        if descriptor['format'] == 'json-members-v1':
            members = at_path(parse_json(data), descriptor['member_field'])
        elif descriptor['format'] == 'csv-column-v1':
            with io.StringIO(data.decode('utf-8-sig'), newline='') as handle:
                reader = csv.DictReader(handle)
                require(reader.fieldnames is not None and reader.fieldnames.count(descriptor['member_field']) == 1,
                        'CSV membership requires exactly one named member column')
                members = [row.get(descriptor['member_field']) for row in reader]
        else:
            raise ValueError('unsupported membership manifest format')
    strings(members, 'membership IDs')
    require(all(member == member.strip() for member in members), 'membership IDs must not be blank or padded')
    return set(members)


def prepare_populations(profile, base):
    profile['_input_base'] = str(base)
    profile['_coverage_inputs'] = []
    profile['_populations'] = {}
    policies = profile.get('assessment_policies', {})
    require(isinstance(policies, dict), 'assessment_policies must be an object keyed by policy ID')
    for identity, policy in policies.items():
        require(text(identity), 'assessment policy ID is required')
        object_fields(policy, ['check_id', 'check_revision', 'method', 'scope', 'target', 'context_id',
                               'population_ref', 'source_config_binding', 'task', 'authority_refs'], 'assessment policy')
        require(text(policy['task']) and isinstance(policy['authority_refs'], list) and bool(policy['authority_refs']),
                'assessment policy requires actual task and source authority')
        for reference in policy['authority_refs']:
            object_fields(reference, ['source_id', 'locator', 'criterion', 'path', 'sha256'], 'policy source reference')
            require(all(text(reference[field]) for field in ('source_id', 'locator', 'criterion')), 'policy source identity/locator/criterion required')
            _, data = bound_file(reference, base, profile['_coverage_inputs'], 'policy source reference', with_bytes=True)
            require(reference['criterion'] in data.decode('utf-8'), 'policy criterion must quote its hashed source bytes')
    policy = profile['coverage_policy']
    if not isinstance(policy, dict):
        return
    contexts, populations = policy.get('contexts', {}), policy.get('populations', {})
    require(isinstance(contexts, dict) and isinstance(populations, dict), 'coverage contexts/populations must be objects')
    bindings = [profile['source_config_binding'], *profile.get('source_config_bindings', [])]
    for context_id, context in contexts.items():
        object_fields(context, ['scope', 'source_config_binding'], 'coverage context')
        require(text(context_id) and text(context['scope']) and context['source_config_binding'] in bindings,
                'coverage context requires an exact declared scope/binding')
    for population_ref, population in populations.items():
        object_fields(population, ['target_unit', 'scope_kind', 'population_role', 'context_id', 'total',
                                  'selection_basis', 'provenance'], 'coverage population')
        require(text(population_ref) and text(population['target_unit']) and text(population['population_role'])
                and text(population['selection_basis']), 'population identity, role and selection basis are required')
        require(population['scope_kind'] in ('sitewide', 'declared-selection', 'named-resource', 'review-case'),
                'unknown population scope_kind')
        require(population['context_id'] in contexts, 'population links unknown context')
        members = member_set(population, 'members', 'membership_manifest', base, profile['_coverage_inputs'])
        require(type(population['total']) is int and population['total'] > 0
                and population['total'] == len(members), 'population total must equal its nonempty unique member set')
        bound_file(population['provenance'], base, profile['_coverage_inputs'], 'population provenance')
        references = population.get('required_input_refs', [])
        require(isinstance(references, list) and (population['scope_kind'] != 'review-case' or bool(references)),
                'review-case requires actual nonempty input references')
        ids = set()
        for reference in references:
            object_fields(reference, ['id', 'path', 'sha256', 'purpose'], 'population input reference')
            require(text(reference['id']) and reference['id'] not in ids and text(reference['purpose']),
                    'input references require unique IDs and an actual purpose')
            ids.add(reference['id'])
            bound_file(reference, base, profile['_coverage_inputs'], 'population input reference')
        profile['_populations'][population_ref] = {'record': population, 'members': members,
                                                 'context': contexts[population['context_id']]}


def profile_data(path):
    path = regular(path)
    profile = load(path)
    object_fields(profile, PROFILE_FIELDS, 'site profile')
    require(type(profile['schema_version']) is int and profile['schema_version'] == 1, 'profile schema_version must be 1')
    require(isinstance(profile['site_id'], str) and SITE_ID.fullmatch(profile['site_id']), 'site_id must be lowercase kebab-case')
    require(path.name == 'profile.json' and path.parent.name == profile['site_id'], 'profile must be sites/<site-id>/profile.json')
    strings(profile['origins'], 'origins', True)
    for origin in profile['origins']:
        parsed = urlsplit(origin)
        require(parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment, 'invalid credential-free origin')
        require(parsed.path in ('', '/'), 'origin must not include a path')
    require(isinstance(profile['allowed_targets'], list) and bool(profile['allowed_targets']), 'allowed_targets must be a nonempty array')
    for target in profile['allowed_targets']:
        require(text(target) or isinstance(target, dict) and text(target.get('target')), 'allowed target requires a string or target object')
        if isinstance(target, dict) and 'recursive' in target:
            require(type(target['recursive']) is bool, 'allowed target recursive must be boolean')
            if target['recursive']:
                root = Path(target['target'])
                require(root.is_absolute() and '..' not in root.parts, 'recursive source root must be absolute without parent traversal')
                require(safe(root).is_dir(), 'recursive source root must be an existing physical directory')
    for field in ('source_selectors', 'publisher', 'templates', 'locale_market_facts', 'capability_facts', 'action_scope', 'input_locators', 'account_property_locators', 'coverage_policy'):
        require(isinstance(profile[field], (dict, list)), field + ' must be a structured object or array')
    strings(profile['issue_refs'], 'issue_refs')
    validate_binding(profile['source_config_binding'], profile['site_id'])
    bindings = profile.get('source_config_bindings', [])
    require(isinstance(bindings, list), 'source_config_bindings must be an array')
    for binding in bindings:
        validate_binding(binding, profile['site_id'])
    prepare_populations(profile, path.parent)
    # The canonical folder/identity equality above prevents duplicate enrollment.
    # Parsing unrelated peers here made one malformed site poison every healthy one.
    return profile


def source_rows(coverage):
    # Research metadata is preserved, not translated into executed site checks.
    rows = coverage.get('sources', coverage.get('dispositions'))
    require(isinstance(rows, list), 'source coverage requires a sources array')
    return rows


def package_data(package):
    package = safe(package)
    registry_path = regular(package / 'references/checks.json')
    source_path = regular(package / 'references/source-coverage.json')
    registry, coverage = load(registry_path), load(source_path)
    object_fields(registry, ['schema_version', 'registry_version', 'generated_at', 'sources_digest', 'checks'], 'registry')
    require(type(registry['schema_version']) is int and registry['schema_version'] == 1, 'registry schema_version must be 1')
    require(text(registry['registry_version']), 'registry_version is required')
    if isinstance(registry['generated_at'], str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', registry['generated_at']):
        datetime.strptime(registry['generated_at'], '%Y-%m-%d')  # metadata precision only
    else:
        when(registry['generated_at'])
    require(registry['sources_digest'] == sha(source_path), 'registry source-coverage digest mismatch')
    require(isinstance(coverage, dict) and coverage.get('schema_version') == 1, 'source coverage requires schema_version 1')
    require(isinstance(registry['checks'], list) and bool(registry['checks']), 'registry requires checks')
    checks, semantic, aliases = {}, set(), set()
    for check in registry['checks']:
        object_fields(check, CHECK_FIELDS, 'registry check')
        for field in ('id', 'semantic_key', 'title', 'category'):
            require(text(check[field]), 'check ' + field + ' is required')
        require(check['id'] not in checks, 'duplicate check id: ' + check['id'])
        require(check['semantic_key'] not in semantic, 'duplicate semantic_key: ' + check['semantic_key'])
        semantic.add(check['semantic_key'])
        require(type(check['revision']) is int and check['revision'] > 0 or text(check['revision']), 'check revision must be positive integer or a version string')
        require(check['kind'] in CLASSES, 'unknown execution class')
        for field in ('capability_ids', 'mechanism_ids', 'aliases', 'upstream_source_ids'):
            strings(check[field], field)
        for alias in [check['id'], *check['aliases']]:
            require(alias not in aliases, 'duplicate check id or alias: ' + alias)
            aliases.add(alias)
        require(isinstance(check['inputs'], list), 'inputs must be an array of native actor descriptions or typed input locators')
        for item in check['inputs']:
            require(text(item) or isinstance(item, dict), 'input must be a description or object')
            if isinstance(item, dict) and 'required' in item:
                require(type(item['required']) is bool, 'input required must be boolean')
            if isinstance(item, dict) and 'profile_path' in item:
                require(text(item['profile_path']), 'input profile_path must be a nonempty dot path')
        require(isinstance(check['evidence_requirement'], dict), 'evidence_requirement must be an object')
        require(isinstance(check['expiry'], dict), 'expiry must be an object')
        age = check['expiry'].get('max_age_seconds_or_null')
        require(age is None or type(age) in (int, float) and math.isfinite(age) and age >= 0, 'expiry max age must be null or nonnegative finite seconds')
        requirements = check['evidence_requirement']
        for field in ('facets', 'accepted_artifact_types', 'required_binding_fields'):
            if field in requirements:
                strings(requirements[field], 'evidence_requirement.' + field)
        if 'population_scope' in requirements:
            strings(requirements['population_scope'], 'population_scope', True)
            require(all(scope in ('sitewide', 'declared-selection', 'named-resource', 'review-case') for scope in requirements['population_scope']), 'unknown required population scope')
            require(text(requirements.get('population_role')), 'typed population requires an explicit semantic population_role')
        conditional = requirements.get('conditional_binding_fields', [])
        require(isinstance(conditional, list), 'conditional_binding_fields must be an array')
        for block in conditional:
            object_fields(block, ['when', 'fields', 'discriminator'], 'conditional binding block')
            object_fields(block['when'], ['artifact_field', 'equals'], 'conditional binding when')
            require(text(block['when']['artifact_field']) and text(block['when']['equals']), 'conditional binding selector requires field and mode')
            strings(block['fields'], 'conditional binding fields', True)
            object_fields(block['discriminator'], ['required', 'allowed_values', 'missing_or_unknown'], 'binding discriminator')
            require(block['discriminator']['required'] is True and block['discriminator']['missing_or_unknown'] == 'unverified', 'binding discriminator must fail closed')
            strings(block['discriminator']['allowed_values'], 'binding discriminator allowed_values', True)
            require(block['when']['equals'] in block['discriminator']['allowed_values'], 'conditional mode must be in discriminator allowed_values')
        if 'window_policy' in requirements:
            require(isinstance(requirements['window_policy'], dict) and requirements['window_policy'].get('mode') in ('snapshot', 'complete', 'method-defined'), 'window_policy requires snapshot, complete or method-defined mode')
        if 'min_window_days' in requirements:
            require(requirements['min_window_days'] is None or type(requirements['min_window_days']) in (int, float) and math.isfinite(requirements['min_window_days']) and requirements['min_window_days'] > 0, 'min_window_days must be null or positive finite days')
        checks[check['id']] = check
    sources = {}
    for source in source_rows(coverage):
        object_fields(source, ['source_id', 'check_ids', 'disposition'], 'source disposition')
        require(text(source['source_id']) and source['source_id'] not in sources, 'duplicate or missing source_id')
        strings(source['check_ids'], 'source check_ids')
        require(all(check_id in checks for check_id in source['check_ids']), 'source links unknown check')
        require(source['disposition'] != 'rule-extracted' or bool(source['check_ids']), 'extracted source rule has no check')
        require(isinstance(source.get('conflicts', []), list), 'source conflicts must be an array')
        for conflict in source.get('conflicts', []):
            if isinstance(conflict, dict) and 'check_ids' in conflict:
                strings(conflict['check_ids'], 'scoped conflict check_ids', True)
                require(all(check_id in checks for check_id in conflict['check_ids']), 'source conflict links unknown check')
        sources[source['source_id']] = source
    for check in checks.values():
        require(all(source in sources for source in check['upstream_source_ids']), 'check links unknown source: ' + check['id'])
    for rule in coverage.get('selected_rules', []):
        require(isinstance(rule, dict), 'selected rule must be an object')
        ids = rule.get('check_ids', [])
        strings(ids, 'selected rule check_ids')
        require(all(check_id in checks for check_id in ids), 'selected rule links unknown check')
        require(bool(ids) or text(rule.get('reason')), 'unrepresented selected source rule')
    # Optional routing graph references remain typed and validated when supplied.
    for filename, array, field in [('capabilities.json', 'capabilities', 'capability_ids')]:
        path = package / 'references' / filename
        if path.exists():
            routes = load(path)
            require(isinstance(routes, dict) and isinstance(routes.get(array), list), 'invalid capability graph')
            known = {row.get('id') for row in routes[array] if isinstance(row, dict)}
            require(all(item in known for check in checks.values() for item in check[field]), 'check links unknown capability')
    return registry, coverage, checks, sources


def is_allowed(profile, target):
    if not text(target):
        return False
    for entry in profile['allowed_targets']:
        candidate = entry if isinstance(entry, str) else entry['target']
        if isinstance(entry, dict) and entry.get('recursive') is True:
            root, selected = Path(candidate), Path(target)
            if not selected.is_absolute() or '..' in selected.parts:
                continue
            # Reject links before resolving; physical ancestry never follows a
            # symlink into another project or collapses a parent traversal.
            root = safe(root).resolve(strict=True)
            selected = safe(selected).resolve(strict=True)
            if selected == root or root in selected.parents:
                return True
            continue
        if target == candidate:
            return True
        parsed, base = urlsplit(target), urlsplit(candidate)
        if base.scheme in ('http', 'https') and parsed.scheme == base.scheme and parsed.netloc == base.netloc and parsed.path.startswith(base.path.rstrip('/') + '/') and not parsed.username and not parsed.password:
            return True
    return False


def at_path(value, path):
    for field in path.split('.'):
        if not isinstance(value, dict) or field not in value:
            return None
        value = value[field]
    return value


def known(value):
    if value is None or value == '' or value == 'unknown':
        return False
    if isinstance(value, dict):
        return bool(value) and all(known(item) for item in value.values())
    if isinstance(value, list):
        return bool(value) and all(known(item) for item in value)
    return True


def evidence_data(path, profile, profile_path, registry, checks, as_of):
    evidence = load(path)
    object_fields(evidence, ['schema_version', 'site_id', 'profile_sha256', 'registry_version', 'as_of', 'artifacts', 'observations'], 'evidence manifest')
    require(type(evidence['schema_version']) is int and evidence['schema_version'] == 1, 'evidence schema_version must be 1')
    require(evidence['site_id'] == profile['site_id'], 'evidence site_id mismatch')
    require(evidence['profile_sha256'] == sha(profile_path), 'evidence profile SHA256 mismatch')
    require(evidence['registry_version'] == registry['registry_version'], 'evidence registry version mismatch')
    require(when(evidence['as_of']) == as_of, 'evidence as_of differs from requested run time')
    require(isinstance(evidence['artifacts'], list) and isinstance(evidence['observations'], list), 'evidence artifacts/observations must be arrays')
    artifacts = {}
    for artifact in evidence['artifacts']:
        object_fields(artifact, ARTIFACT_FIELDS, 'artifact')
        require(text(artifact['id']) and artifact['id'] not in artifacts, 'duplicate or missing artifact id')
        require(text(artifact['path']), 'artifact path is required')
        artifact_path = Path(artifact['path'])
        if not artifact_path.is_absolute():
            artifact_path = path.parent / artifact_path
        artifact_path = regular(artifact_path)
        require(isinstance(artifact['sha256'], str) and HASH.fullmatch(artifact['sha256']) and sha(artifact_path) == artifact['sha256'], 'artifact SHA256 mismatch: ' + artifact['id'])
        when(artifact['observed_at'])
        require(text(artifact['collector']) and text(artifact['collector_version']), 'artifact collector/version required')
        require(isinstance(artifact['source_config_binding'], dict) and isinstance(artifact['coverage'], dict), 'artifact binding/coverage must be objects')
        require(isinstance(artifact['limitations'], list), 'artifact limitations must be an array')
        if 'facets' in artifact:
            strings(artifact['facets'], 'artifact facets')
        artifact = dict(artifact, resolved_path=str(artifact_path), _input_base=str(path.parent), _coverage_inputs=[])
        if any(field in artifact['coverage'] for field in ('observed_members', 'observed_membership_manifest')):
            artifact['_observed_members'] = member_set(artifact['coverage'], 'observed_members',
                                                      'observed_membership_manifest', path.parent,
                                                      artifact['_coverage_inputs'])
        artifacts[artifact['id']] = artifact
    evidence['_applicability_inputs'] = []
    for observation in evidence['observations']:
        object_fields(observation, OBSERVATION_FIELDS, 'observation')
        require(not any(key.startswith('_retained_') for key in observation), 'retained history metadata is reserved for validated runs')
        require(observation['check_id'] in checks, 'observation links unknown check')
        require(observation['applicability'] in APPLICABILITY and observation['execution'] in EXECUTION and observation['verdict'] in VERDICT, 'invalid observation state')
        require(text(observation['scope']) and text(observation['target']), 'observation scope and target required')
        require(text(observation['reason']) and text(observation['actor']), 'observation reason and actor required')
        strings(observation['artifact_ids'], 'observation artifact_ids')
        require(all(item in artifacts for item in observation['artifact_ids']), 'observation links unknown artifact')
        require(observation['readback'] is None or isinstance(observation['readback'], dict), 'readback must be null or an object')
        require(observation['window'] is None or isinstance(observation['window'], dict), 'window must be null or an object')
        basis = observation.get('applicability_basis')
        if isinstance(basis, dict) and isinstance(basis.get('required_input_refs'), list):
            for reference in basis['required_input_refs']:
                if isinstance(reference, dict) and 'path' in reference and 'sha256' in reference:
                    bound_file(reference, path.parent, evidence['_applicability_inputs'], 'applicability authority input')
    return evidence, artifacts


def default_row(check, reason='No matching observation imported'):
    always = check['applies_if'] == 'always' or check['applies_if'] == {'always': True}
    return {'check_id': check['id'], 'check_revision': check['revision'], 'category': check['category'], 'title': check['title'], 'kind': check['kind'], 'scope': check['evidence_requirement'].get('scope'), 'target': None, 'scoped_results': [], 'population_ref': None, 'context_id': None, 'population_role': None, 'population_scope_kind': None, 'temporal_scope': {'claim': 'unverified', 'audit_as_of': None, 'artifacts': []}, 'applicability': 'applicable' if always else 'undetermined', 'execution': 'not-run', 'verdict': 'unknown', 'freshness': 'unverified', 'reasons': [reason], 'observations': [], 'artifact_ids': [], 'pending_readback': False, 'preserved_effects': []}


def coverage_errors(artifact, requirements, profile):
    result = []
    coverage = artifact['coverage']
    total, observed = coverage.get('total'), coverage.get('observed')
    if not (type(total) is int and total > 0 and type(observed) is int and 0 < observed <= total):
        result.append('Missing or invalid nonempty coverage denominator')
        return result
    if coverage.get('target_unit') != requirements.get('target_unit'):
        result.append('Coverage target unit mismatch')
    population_ref = coverage.get('population_ref')
    typed = 'population_scope' in requirements
    if typed or population_ref is not None:
        if not typed:
            return result + ['Referenced population requires an explicit check population_scope']
        population = profile.get('_populations', {}).get(population_ref)
        if population is None:
            return result + ['Missing or unknown explicit population_ref']
        declared = population['record']
        if (declared['target_unit'] != coverage.get('target_unit')
                or declared['population_role'] != requirements['population_role']
                or declared['scope_kind'] not in requirements['population_scope']):
            result.append('Population unit/role/scope does not satisfy the check assertion universe')
        if coverage.get('context_id') != declared['context_id']:
            result.append('Population context differs from artifact coverage context')
        if total != declared['total']:
            result.append('Coverage denominator differs from the named population')
        members = artifact.get('_observed_members')
        if members is None:
            result.append('Missing actual observed member set')
        elif len(members) != observed or not members.issubset(population['members']):
            result.append('Observed member identities/count differ from the declared population')
        elif coverage.get('mode') == 'full' and members != population['members']:
            result.append('Full evidence must cover exactly every declared member')
        expected = requirements.get('expected_coverage')
        mode = expected.get('mode') if isinstance(expected, dict) else expected
        if mode not in ('full', 'sample'):
            result.append('No typed full/sample acceptance coverage policy')
        elif mode == 'full' and (coverage.get('mode') != 'full' or observed != total):
            result.append('Sample evidence cannot establish whole-population coverage')
        elif mode == 'sample' and coverage.get('mode') not in ('full', 'sample'):
            result.append('Unknown sample coverage')
        if isinstance(expected, dict) and type(expected.get('minimum')) is int and observed < expected['minimum']:
            result.append('Sample below required minimum')
        return result
    policy = profile['coverage_policy']
    units = policy.get('units', {}) if isinstance(policy, dict) else {}
    declared_total = units.get(coverage.get('target_unit'))
    expected = requirements.get('expected_coverage')
    if declared_total is None and isinstance(expected, dict):
        declared_total = expected.get('total')
    if declared_total is not None and (type(declared_total) is not int or declared_total <= 0 or total != declared_total):
        result.append('Coverage denominator differs from declared site/check population')
    mode = expected.get('mode') if isinstance(expected, dict) else expected
    if mode not in ('full', 'sample'):
        result.append('No typed full/sample acceptance coverage policy')
    elif mode == 'full' and declared_total is None:
        result.append('Whole-population coverage lacks authoritative site/check denominator')
    elif mode == 'full' and (coverage.get('mode') != 'full' or observed != total):
        result.append('Sample evidence cannot establish whole-population coverage')
    elif mode == 'sample' and coverage.get('mode') not in ('full', 'sample'):
        result.append('Unknown sample coverage')
    if isinstance(expected, dict) and type(expected.get('minimum')) is int and observed < expected['minimum']:
        result.append('Sample below required minimum')
    return result


def unresolved(check, sources):
    conflicts = list(check.get('conflicts', []))
    for source in check['upstream_source_ids']:
        if sources[source]['disposition'] == 'unresolved-conflict':
            return True
        conflicts.extend(sources[source].get('conflicts', []))
    for conflict in conflicts:
        if isinstance(conflict, dict) and 'check_ids' in conflict:
            # Scoped rule decisions do not spill into unrelated assertions merely
            # because both checks cite the same broad research dossier.
            if isinstance(conflict['check_ids'], list) and conflict['check_ids'] and check['id'] not in conflict['check_ids']:
                continue
        if not isinstance(conflict, dict) or conflict.get('status') not in ('resolved', 'superseded'):
            return True
    return False


def explicit_missing_inputs(check, profile):
    return [item.get('name', item['profile_path']) for item in check['inputs'] if isinstance(item, dict) and item.get('required') is True and text(item.get('profile_path')) and not known(at_path(profile, item['profile_path']))]


def missing_account(check, profile):
    if check['kind'] != 'account':
        return False
    fields = check['evidence_requirement'].get('required_binding_fields', [])
    property_keys = [field.split('.')[1] for field in fields if isinstance(field, str) and field.startswith('account_properties.') and len(field.split('.')) >= 2]
    locators = profile['account_property_locators']
    return not property_keys or not isinstance(locators, dict) or any(not known(locators.get(key)) for key in property_keys)


def assess_applicability(check, observation, artifacts, profile, as_of, sources):
    row = default_row(check)
    row.update(applicability='undetermined', execution='blocked' if missing_account(check, profile) or explicit_missing_inputs(check, profile) else 'not-run',
               scope=observation['scope'], target=observation['target'], artifact_ids=observation['artifact_ids'], observations=[observation])
    errors = []
    basis = observation.get('applicability_basis')
    condition = check['applies_if'].get('statement') if isinstance(check['applies_if'], dict) else None
    if not isinstance(basis, dict):
        row['reasons'] = [observation['reason'], 'Missing explicit applicability-only authority proof']
        return row
    always = check['applies_if'] == 'always' or isinstance(check['applies_if'], dict) and check['applies_if'].get('always') is True
    source_condition = check['applies_if'].get('source_condition') if isinstance(check['applies_if'], dict) else None
    if always or not text(condition) or basis.get('condition_statement') != condition or condition == source_condition:
        errors.append('N/A must prove the exact substantive conditional predicate false; always/readiness cannot be substituted')
    if basis.get('condition_met') is not False or basis.get('reason_kind') != 'domain-fact':
        errors.append('Missing access/input/collector/window or an unknown condition is not false domain proof')
    if not observation['artifact_ids'] or basis.get('artifact_ids') != observation['artifact_ids']:
        errors.append('Applicability proof IDs must exactly equal the actual observation artifacts')
    authority = basis.get('authority')
    if not isinstance(authority, dict) or authority.get('kind') not in ('complete-owned-source', 'authoritative-owned-inventory', 'owning-product-contract') or authority.get('complete') is not True or not text(authority.get('boundary')):
        errors.append('Missing complete owned authority kind, actual boundary and version')
    refs = basis.get('required_input_refs')
    if not isinstance(refs, list) or not refs:
        errors.append('Actual complete authority input references are required')
        refs = []
    inputs, ids = [], set()
    base = next((artifact.get('_input_base') for artifact in artifacts.values() if artifact.get('_input_base')), profile.get('_input_base', Path.cwd()))
    for reference in refs:
        if not isinstance(reference, dict) or not all(field in reference for field in ('id', 'path', 'sha256', 'purpose')) or not text(reference.get('id')) or reference.get('id') in ids or not text(reference.get('purpose')):
            errors.append('Authority inputs require unique IDs, actual paths/hashes and purpose')
            continue
        ids.add(reference['id'])
        bound_file(reference, base, inputs, 'applicability authority input')
    facts = basis.get('facts')
    if not isinstance(facts, list) or not facts:
        errors.append('Actual cited facts supporting the false predicate are required')
        facts = []
    fact_ids = set()
    for fact in facts:
        if not isinstance(fact, dict) or fact.get('artifact_id') not in observation['artifact_ids'] or not text(fact.get('locator')) or not text(fact.get('statement')):
            errors.append('Fact citations require an actual proof artifact, exact locator and supported statement')
        else:
            fact_ids.add(fact['artifact_id'])
    if fact_ids != set(observation['artifact_ids']):
        errors.append('Every applicability proof artifact needs an actual fact citation')
    policy = profile['coverage_policy']
    contexts = policy.get('contexts', {}) if isinstance(policy, dict) else {}
    context = contexts.get(basis.get('context_id'))
    if not isinstance(context, dict):
        errors.append('Applicability proof must select an existing exact context')
    else:
        binding = context['source_config_binding']
        expected = observation.get('source_config_binding', profile['source_config_binding'])
        if context['scope'] != observation['scope'] or expected != binding:
            errors.append('Applicability observation scope/binding differs from its selected context')
        if context['scope'] != check['evidence_requirement'].get('scope'):
            errors.append('Source-only absence cannot settle a different or unknown production applicability scope')
        for artifact_id in observation['artifact_ids']:
            artifact = artifacts[artifact_id]
            if artifact.get('scope') != context['scope'] or artifact['source_config_binding'] != binding:
                errors.append('All applicability artifacts must match the exact selected site/source/context')
        source = binding['source']
        immutable = source['kind'] in ('commit', 'tree') and known(source.get('revision')) or source['kind'] == 'files' and known(source.get('files_sha256'))
        source_authority = isinstance(authority, dict) and authority.get('kind') in ('complete-owned-source', 'authoritative-owned-inventory')
        if source_authority and context['scope'] not in ('source', 'package'):
            equivalent = immutable and known(source.get('revision')) and known(binding['serving'].get('source_tree')) and known(binding.get('config_sha256')) and known(binding['serving'].get('revision')) and binding['serving']['source_tree'] == source['revision']
            if not equivalent:
                errors.append('Unbound source absence cannot establish production absence')
        if source_authority and not immutable:
            errors.append('Owned source/inventory absence requires a known immutable source boundary')
        if source.get('files_sha256') and (source_authority or context['scope'] in ('source', 'package') and immutable):
            for name, expected_hash in source['files_sha256'].items():
                key = Path(name)
                covered = any(reference.get('sha256') == expected_hash and (reference.get('id') == name or (Path(reference['path']) == key if key.is_absolute() else tuple(Path(reference['path']).parts[-len(key.parts):]) == key.parts)) for reference in refs if isinstance(reference, dict) and text(reference.get('path')))
                if not covered:
                    errors.append('Complete source authority must include every file in the closed immutable boundary')
    if observation.get('readback'):
        errors.append('Applicability N/A is not an observed-fixed transition')
    if errors:
        row['reasons'] = [observation['reason'], *dict.fromkeys(errors)]
        return row
    # Reuse the ordinary identity/time/conflict/effect validator. Only positive
    # execution coverage, facets, account readiness and outcome windows differ.
    proof_check = dict(check, kind='expert', inputs=[])
    fields = ['site_id']
    if context['scope'] in ('source', 'package') and immutable:
        fields += ['source.kind', 'source.files_sha256' if source['kind'] == 'files' else 'source.revision']
        proof_check['expiry'] = {'basis': 'immutable-input-bindings', 'max_age_seconds_or_null': None}
    else:
        fields += ['serving.origin']
    proof_check['evidence_requirement'] = {'scope': context['scope'], 'facets': ['applicability-fact'],
        'required_binding_fields': fields, 'accepted_artifact_types': list(dict.fromkeys(artifacts[item].get('artifact_type') for item in observation['artifact_ids'] if text(artifacts[item].get('artifact_type'))))}
    proof = dict(observation, applicability='applicable', execution='completed', verdict='unknown', window=None, readback=None)
    assessed = assess(proof_check, proof, artifacts, profile, as_of, sources, proof_only=True)
    assessed.update(kind=check['kind'], observations=[observation], verdict='unknown', population_ref=None,
                    context_id=basis['context_id'], population_role=None, population_scope_kind=None,
                    applicability_proof={'condition_statement': condition, 'reason_kind': 'domain-fact',
                        'scope': context['scope'], 'context_id': basis['context_id'], 'authority': authority,
                        'required_input_refs': refs, 'facts': facts})
    if assessed['freshness'] in ('current', 'dated'):
        assessed.update(applicability='not-applicable', execution='not-run')
        assessed['reasons'].append('False domain condition proven only in the stated authority scope; positive execution was not run')
    else:
        assessed.update(applicability='undetermined', execution=row['execution'])
    return assessed


def assessment_policy(check, observation, artifacts, profile, row):
    """Native source/task qualification, never a boolean grant or substitute for data."""
    identity = observation.get('assessment_policy_id')
    if identity is None:
        return {}, []
    try:
        policy = profile.get('assessment_policies', {}).get(identity)
        require(isinstance(policy, dict), 'unknown assessment_policy_id')
        for field, expected in [('check_id', check['id']), ('check_revision', observation['check_revision']),
                                ('method', check['method']), ('scope', observation['scope']),
                                ('target', observation['target']), ('context_id', row['context_id']),
                                ('population_ref', row['population_ref']),
                                ('source_config_binding', observation.get('source_config_binding', profile['source_config_binding']))]:
            require(policy[field] == expected, 'assessment policy differs from exact ' + field)
        require(observation['check_revision'] == check['revision'], 'assessment policy uses old check revision')
        for reference in policy['authority_refs']:
            kind = reference.get('authority_kind', 'upstream-source')
            require(kind in ('upstream-source', 'task-instruction'), 'unknown policy authority kind')
            if kind == 'task-instruction':
                require(text(policy.get('task_id')) and reference['source_id'] == policy['task_id'], 'task policy authority must identify its exact task instruction')
            else:
                require(reference['source_id'] in check['upstream_source_ids'], 'policy source is not an upstream authority for this check')
        source_criteria = {reference['criterion'] for reference in policy['authority_refs']}
        timing = policy.get('timeliness', {})
        require(isinstance(timing, dict), 'policy timeliness must be an object')
        if timing:
            object_fields(timing, ['mode', 'data_basis', 'rationale', 'criterion'], 'policy timeliness')
            require(timing['criterion'] in source_criteria, 'timeliness criterion needs its exact quoted source authority')
            require(timing['mode'] in ('dated-snapshot', 'max-age') and timing['data_basis'] == 'oldest-supporting-data' and text(timing['rationale']), 'policy timeliness must preserve oldest actual data date')
            if timing['mode'] == 'max-age':
                age = timing.get('max_age_seconds')
                require(type(age) in (int, float) and math.isfinite(age) and age > 0, 'qualified maximum age must be explicit positive finite seconds')
            else:
                require(timing.get('max_age_seconds') is None, 'dated policy cannot grant a TTL')
        window = policy.get('window', {})
        require(isinstance(window, dict), 'policy window must be an object')
        if window:
            object_fields(window, ['mode', 'min_window_days', 'minimum_basis', 'rationale', 'acceptance_criteria'], 'policy window')
            require(window['mode'] == check['evidence_requirement'].get('window_policy', {}).get('mode') and window['mode'] in ('complete', 'method-defined'), 'policy window mode differs from check method')
            minimum = window['min_window_days']
            require((minimum is None and window['minimum_basis'] == 'no-duration-minimum') or
                    (type(minimum) in (int, float) and math.isfinite(minimum) and minimum > 0 and window['minimum_basis'] == 'explicit-source-minimum'), 'policy minimum requires explicit source/task rationale; no invented universal minimum')
            require(text(window['rationale']), 'policy window rationale required')
            strings(window['acceptance_criteria'], 'policy window acceptance criteria', True)
            require(set(window['acceptance_criteria']).issubset(source_criteria), 'window criteria need exact quoted source authority')
            actual = observation.get('window', {}).get('assessment') if isinstance(observation.get('window'), dict) else None
            object_fields(actual, ['method', 'acceptance', 'criteria', 'input_results', 'rationale'], 'actual window assessment')
            require(actual['method'] == check['method'] and actual['acceptance'] == check['acceptance'], 'actual window assessment must use exact check method/acceptance')
            require(text(actual['rationale']), 'actual window assessment needs a substantive native rationale')
            require(isinstance(actual['input_results'], list) and len(actual['input_results']) == len(check['inputs']), 'actual method assessment must cover every exact check input')
            referenced_fields, input_fields = set(), []
            for index, result in enumerate(actual['input_results']):
                object_fields(result, ['input', 'assessment', 'data_refs'], 'actual method input result')
                require(result['input'] == check['inputs'][index] and text(result['assessment']), 'method input and native assessment must match the exact check input')
                require(isinstance(result['data_refs'], list) and bool(result['data_refs']), 'method input requires actual structured data fields')
                selected_fields = set()
                for reference in result['data_refs']:
                    object_fields(reference, ['artifact_id', 'format', 'locator', 'value_sha256'], 'method input data reference')
                    require(reference['artifact_id'] in observation['artifact_ids'] and reference['format'] == 'json-field-v1' and text(reference['locator']), 'method input requires selected JSON field data')
                    artifact = artifacts[reference['artifact_id']]
                    require(reference['locator'].split('.')[0] not in ('members', 'coverage', 'provenance', 'fixture'), 'membership/provenance is not substantive method data')
                    field = at_path(parse_json(regular(artifact['resolved_path']).read_bytes()), reference['locator'])
                    require(isinstance(field, dict) and bool(field) or isinstance(field, list) and bool(field) and all(isinstance(item, dict) and bool(item) for item in field), 'method data field must contain actual nonempty structured values')
                    value_hash = hashlib.sha256(json.dumps(field, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()).hexdigest()
                    require(reference['value_sha256'] == value_hash, 'method input field hash differs from actual data')
                    selected_fields.add((reference['artifact_id'], reference['locator']))
                input_fields.append(selected_fields)
                referenced_fields.update(selected_fields)
            require(len(referenced_fields) >= len(check['inputs']), 'method inputs cannot all point to the same generic field')
            require(all(fields - set().union(*(other for number, other in enumerate(input_fields) if number != index)) for index, fields in enumerate(input_fields)), 'each method input needs its own distinct actual field')
            require(isinstance(actual['criteria'], list) and len(actual['criteria']) == len(window['acceptance_criteria']), 'every source/task window criterion needs actual method data')
            results, statements, used_inputs = [], [], set()
            for criterion in actual['criteria']:
                object_fields(criterion, ['statement', 'result', 'input_indices', 'rationale'], 'actual criterion')
                statements.append(criterion['statement']); results.append(criterion['result'])
                require(criterion['result'] in ('pass', 'fail') and text(criterion['rationale']), 'criterion requires observed result and substantive native rationale')
                require(isinstance(criterion['input_indices'], list) and bool(criterion['input_indices']) and all(type(index) is int and 0 <= index < len(check['inputs']) for index in criterion['input_indices']), 'criterion must cite actual method input results')
                used_inputs.update(criterion['input_indices'])
            require(used_inputs == set(range(len(check['inputs']))), 'window criteria must assess every exact method input')
            require(len(set(statements)) == len(statements) and set(statements) == set(window['acceptance_criteria']), 'actual criterion statements differ from the source/task policy')
            require(observation['verdict'] == ('fail' if 'fail' in results else 'pass'), 'observation verdict differs from actual criterion results')
        require(bool(timing or window), 'assessment policy must qualify timeliness or window')
        row['temporal_scope']['assessment_policy_id'] = identity
        return policy, []
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        return {}, ['Invalid source/task assessment qualification: ' + str(exc)]


def assess(check, observation, artifacts, profile, as_of, sources, proof_only=False):
    if observation['applicability'] == 'not-applicable' and not proof_only:
        return assess_applicability(check, observation, artifacts, profile, as_of, sources)
    row = default_row(check)
    row.update({key: observation[key] for key in ('applicability', 'execution', 'verdict', 'artifact_ids', 'scope', 'target')})
    row['reasons'] = []
    row['observations'] = [observation]
    row['temporal_scope'] = {'claim': 'unverified', 'audit_as_of': as_of.isoformat(), 'artifacts': [], 'window': observation.get('window'), 'data_as_of': observation.get('data_as_of')}
    requirements = check['evidence_requirement']
    profile_coverage = profile['coverage_policy'] if isinstance(profile['coverage_policy'], dict) else {}
    selected = [artifacts[item] for item in observation['artifact_ids']]
    mismatch, stale, unverified = [], [], []
    if observation['check_revision'] != check['revision']:
        mismatch.append('Check revision differs from current registry')
    if '_retained_check' in observation and (observation['_retained_check'] != check or
            observation.get('_retained_sources') != {identity: sources[identity] for identity in check['upstream_source_ids']}):
        mismatch.append('Retained failure check/source contract differs from current registry')
    expected_binding = observation.get('source_config_binding', profile['source_config_binding'])
    declared_bindings = [profile['source_config_binding'], *profile.get('source_config_bindings', [])]
    if expected_binding not in declared_bindings:
        mismatch.append('Observation selects an undeclared source/config/serving context')
    if not is_allowed(profile, observation['target']):
        mismatch.append('Observation target outside selected site allowed targets')
    expected_scope = requirements.get('scope')
    if not text(expected_scope) or observation['scope'] != expected_scope:
        mismatch.append('Observation scope differs from check scope')
    required_fields = requirements.get('required_binding_fields')
    if not isinstance(required_fields, list) or not required_fields:
        unverified.append('No required binding fields declared')
        required_fields = ['site_id']
    for field in required_fields:
        if not known(at_path(expected_binding, field)):
            unverified.append('Unknown required binding field: ' + field)
    if not selected:
        unverified.append('No actual artifact supports this observation')
    population_keys = {(artifact['coverage'].get('population_ref'), artifact['coverage'].get('context_id')) for artifact in selected}
    if 'population_scope' in requirements and len(population_keys) > 1:
        mismatch.append('All evidence facets must describe the same population/context')
    if len(population_keys) == 1:
        row['population_ref'], row['context_id'] = next(iter(population_keys))
        population = profile.get('_populations', {}).get(row['population_ref'])
        if population is not None:
            row['population_role'] = population['record']['population_role']
            row['population_scope_kind'] = population['record']['scope_kind']
    if '_retained_population' in observation and (observation['_retained_population'] !=
            profile_coverage.get('populations', {}).get(row['population_ref']) or
            observation.get('_retained_context') != profile_coverage.get('contexts', {}).get(row['context_id'])):
        mismatch.append('Retained failure population/context definition differs from current profile')
    if '_retained_policy' in observation and observation['_retained_policy'] != profile.get('assessment_policies', {}).get(observation.get('assessment_policy_id')):
        mismatch.append('Retained failure assessment policy differs from current profile')
    observed_facets = set()
    policy, policy_errors = assessment_policy(check, observation, artifacts, profile, row)
    unverified.extend(policy_errors)
    timeliness = policy.get('timeliness', {})
    snapshot = check['kind'] == 'account' and requirements.get('window_policy', {}).get('mode') == 'snapshot'
    dated_only = (check['expiry'].get('basis') == 'dated-snapshot' or
                  timeliness.get('mode') == 'dated-snapshot' or
                  snapshot and check['expiry'].get('max_age_seconds_or_null') is None and timeliness.get('mode') != 'max-age')
    for artifact in selected:
        population = profile.get('_populations', {}).get(artifact['coverage'].get('population_ref'))
        if population is not None:
            context = population['context']
            if (artifact['source_config_binding'] != context['source_config_binding']
                    or expected_binding != context['source_config_binding']
                    or artifact.get('scope') != context['scope']):
                mismatch.append('Population context must match exact artifact and selected observation scope/binding')
        if artifact['target'] != observation['target'] or artifact.get('scope') != observation['scope']:
            mismatch.append('Artifact target/scope differs from observation')
        # Site identity is unconditional; other comparisons follow selected check fields.
        binding = artifact['source_config_binding']
        if binding.get('site_id') != profile['site_id']:
            mismatch.append('Artifact site identity mismatch')
        conditional_fields = []
        for block in requirements.get('conditional_binding_fields', []):
            mode = at_path(artifact, block['when']['artifact_field'])
            if mode not in block['discriminator']['allowed_values']:
                unverified.append('Missing or unknown required collector discriminator: ' + block['when']['artifact_field'])
            elif mode == block['when']['equals']:
                conditional_fields.extend(block['fields'])
        for field in list(dict.fromkeys(required_fields + conditional_fields)):
            if field.startswith('account_properties.'):
                key = field.split('.')[1]
                locators = profile['account_property_locators']
                if not isinstance(locators, dict) or not known(locators.get(key)):
                    unverified.append('Missing real conditional/unconditional account property locator: ' + key)
                    row['execution'] = 'blocked'
            actual, expected = at_path(binding, field), at_path(expected_binding, field)
            if actual != expected:
                mismatch.append('Artifact source/config binding differs: ' + field)
            elif not known(actual):
                unverified.append('Artifact required binding is unknown: ' + field)
        observed = when(artifact['observed_at'])
        if observed > as_of:
            mismatch.append('Artifact observation is after run as_of')
        # Reading an old provider export today does not make its rank/metric date
        # current. Use the oldest declared data date, never import/fetch time.
        data_dates = [observed]
        window = observation.get('window')
        if isinstance(window, dict):
            for field in ('end', 'observed_at'):
                if window.get(field):
                    data_dates.append(when(window[field]))
        if observation.get('data_as_of'):
            data_dates.append(when(observation['data_as_of']))
        provider_dates = []
        if artifact.get('data_observed_at'):
            provider_dates.append(when(artifact['data_observed_at']))
        if isinstance(artifact.get('data_window'), dict) and artifact['data_window'].get('end'):
            provider_dates.append(when(artifact['data_window']['end']))
        if any(date > observed for date in provider_dates):
            mismatch.append('Provider data date is after supporting artifact collection')
        data_dates.extend(provider_dates)
        if any(date > observed or date > as_of for date in data_dates):
            mismatch.append('Declared data/window date is after collection or audit as_of')
        row['temporal_scope']['artifacts'].append({'artifact_id': artifact['id'], 'observed_at': artifact['observed_at'], 'data_as_of': min(data_dates).isoformat(), 'data_observed_at': artifact.get('data_observed_at'), 'data_window': artifact.get('data_window'), 'provider_dates': [date.isoformat() for date in provider_dates]})
        max_age = check['expiry'].get('max_age_seconds_or_null')
        qualified_age = timeliness.get('max_age_seconds') if timeliness.get('mode') == 'max-age' else None
        if qualified_age is not None:
            max_age = min(max_age, qualified_age) if max_age is not None else qualified_age
        if max_age is not None and (as_of - min(data_dates)).total_seconds() > max_age:
            stale.append('Artifact/provider data window expired under check-specific freshness policy')
        has_data_window = isinstance(window, dict) and window.get('complete') is True and any(window.get(field) for field in ('end', 'observed_at'))
        if check['expiry'].get('temporal_basis') == 'data-window-end' and not provider_dates and not has_data_window:
            unverified.append('Missing actual provider/rank data date or complete source window')
        durable_basis = check['expiry'].get('basis') in ('source-revision', 'source', 'config-revision', 'immutable', 'package-revision', 'immutable-input-bindings')
        immutable_fields = ('source', 'source.revision', 'source.files_sha256', 'config_sha256', 'package_sha256')
        durable_binding = any(field in immutable_fields and known(at_path(expected_binding, field)) for field in required_fields)
        durable_scope = observation['scope'] in ('source', 'package')
        if max_age is None and not dated_only and not (durable_basis and durable_binding and durable_scope):
            unverified.append('No qualified timeliness policy for mutable or current-required evidence; recorded date is historical only')
        observed_facets.update(artifact.get('facets', []))
        accepted = requirements.get('accepted_artifact_types')
        if not isinstance(accepted, list) or not accepted or artifact.get('artifact_type') not in accepted:
            unverified.append('Artifact type not accepted by check')
        if not proof_only:
            unverified.extend(coverage_errors(artifact, requirements, profile))
        effect = artifact.get('effect_status')
        if effect in ('UNKNOWN', 'possibly-sent'):
            unverified.append('Effect outcome is UNKNOWN/possibly-sent; reconcile retained receipt without replay')
        if effect in ('UNKNOWN', 'completed', 'possibly-sent', 'sent'):
            row['preserved_effects'].append({'artifact_id': artifact['id'], 'status': effect, 'replay': False})
    facets = requirements.get('facets')
    if not isinstance(facets, list) or not facets or not set(facets).issubset(observed_facets):
        unverified.append('Required evidence facets are missing')
    required_inputs = explicit_missing_inputs(check, profile)
    if required_inputs:
        unverified.extend('Missing required profile input: ' + name for name in required_inputs)
        row['execution'] = 'blocked'
    account_missing = missing_account(check, profile)
    if account_missing:
        unverified.append('Missing real account/property locator')
        row['execution'] = 'blocked'
    if check['kind'] in ('account', 'longitudinal'):
        window = observation.get('window')
        if snapshot:
            if not isinstance(window, dict) or window.get('complete') is not True or not window.get('observed_at'):
                unverified.append('Missing complete dated account snapshot')
            elif when(window['observed_at']) > as_of or any(when(artifact['observed_at']) < when(window['observed_at']) for artifact in selected):
                mismatch.append('Account snapshot is after run as_of or supporting artifact time')
        elif not isinstance(window, dict) or window.get('complete') is not True or not window.get('start') or not window.get('end'):
            unverified.append('Missing complete account/observation window')
        else:
            start, end = when(window['start']), when(window['end'])
            minimum = requirements.get('min_window_days')
            policy_window = policy.get('window', {})
            if policy_window.get('min_window_days') is not None:
                minimum = max(minimum or 0, policy_window['min_window_days'])
            if end > as_of or start >= end or any(when(artifact['observed_at']) < end for artifact in selected):
                mismatch.append('Window chronology invalid, after as_of or supporting artifact predates its end')
            if minimum is not None and (type(minimum) not in (int, float) or (end - start).total_seconds() < minimum * 86400):
                unverified.append('No adequate check-specific complete observation window')
            mode = requirements.get('window_policy', {}).get('mode')
            if mode == 'method-defined' and not policy_window:
                unverified.append('Missing source/task-qualified method-specific window acceptance policy and data')
            elif minimum is None and mode not in ('complete', 'method-defined'):
                unverified.append('No check-specific complete-window acceptance policy')
    if row['execution'] != 'completed':
        unverified.append('Check execution did not complete')
    if unresolved(check, sources):
        unverified.append('Unresolved substantive source/rule conflict')
    if row['applicability'] == 'not-applicable':
        basis = observation.get('applicability_basis')
        always = check['applies_if'] == 'always' or check['applies_if'] == {'always': True}
        if always or not selected or account_missing or not isinstance(basis, dict) or basis.get('condition_met') is not False or not basis.get('artifact_ids') or not set(basis['artifact_ids']).issubset(observation['artifact_ids']):
            row['applicability'] = 'undetermined'
            unverified.append('Not-applicable contradicts always condition or lacks explicit backed applicability fact')
        row['verdict'] = 'unknown'
    elif row['applicability'] == 'undetermined':
        unverified.append('Applicability remains undetermined')
    readback = observation.get('readback')
    if readback:
        status = readback.get('status')
        if status != 'observed-fixed':
            row['pending_readback'] = True
            unverified.append('Fix has candidate/source proof; matching target readback remains pending')
        else:
            original = readback.get('original_artifact_ids', [])
            back = readback.get('artifact_ids', [])
            fixed_at = readback.get('fixed_at')
            if not original or not back or not fixed_at or set(original) & set(back) or not set(back).issubset(observation['artifact_ids']) or any(item not in artifacts for item in original + back):
                unverified.append('Readback must identify retained original and distinct actual post-fix artifacts')
                row['pending_readback'] = True
            else:
                if any(artifacts[item]['target'] != observation['target'] or artifacts[item].get('scope') != observation['scope'] or artifacts[item]['source_config_binding'].get('site_id') != profile['site_id'] for item in original + back):
                    mismatch.append('Fix readback does not match original failure target/scope/site')
                    row['pending_readback'] = True
                if any((artifacts[item]['coverage'].get('population_ref'), artifacts[item]['coverage'].get('context_id')) != (row['population_ref'], row['context_id']) for item in original + back):
                    mismatch.append('Fix readback cannot replace another population/context')
                    row['pending_readback'] = True
                fixed = when(fixed_at)
                readback_dates = {item['artifact_id']: when(item['data_as_of']) for item in row['temporal_scope']['artifacts']}
                if any(readback_dates[item] < fixed for item in back):
                    unverified.append('Post-fix fetch contains pre-fix provider/data window; target readback is still pending')
                    row['pending_readback'] = True
                if fixed > as_of or any(when(artifacts[item]['observed_at']) >= fixed for item in original) or any(when(artifacts[item]['observed_at']) < fixed for item in back):
                    unverified.append('Readback artifacts do not straddle the recorded fix time')
                    row['pending_readback'] = True
    row['freshness'] = 'binding-mismatch' if mismatch else 'stale' if stale else 'unverified' if unverified else 'dated' if dated_only else 'current'
    row['reasons'] = list(dict.fromkeys([observation['reason'], *mismatch, *stale, *unverified]))
    if row['freshness'] == 'dated':
        row['temporal_scope']['claim'] = 'recorded-date-only'
        row['reasons'].append('Verified only for the recorded target/date/window; current state is not established')
    elif row['freshness'] == 'current':
        row['temporal_scope']['claim'] = 'current-at-as-of'
    if row['freshness'] not in ('current', 'dated'):
        row['verdict'] = 'unknown'
    if observation.get('_retained_resolved') is True and not any(effect['status'] in ('UNKNOWN', 'possibly-sent') for effect in row['preserved_effects']):
        row.update(verdict='unknown', execution='not-run', freshness='unverified', pending_readback=False)
        row['temporal_scope']['claim'] = 'unverified'
        row['reasons'].append('Preserved resolved effect receipt only; this is not a new domain observation or unresolved failure')
    return row


def matrix(checks, sources, evidence, artifacts, profile, as_of):
    groups = {}
    for observation in evidence.get('observations', []):
        groups.setdefault(observation['check_id'], []).append(observation)
    rows = []
    for check in checks.values():
        observations = groups.get(check['id'], [])
        if not observations:
            row = default_row(check)
            if missing_account(check, profile):
                row['execution'] = 'blocked'; row['reasons'].append('Missing real account/property locator')
            for name in explicit_missing_inputs(check, profile):
                row['execution'] = 'blocked'; row['reasons'].append('Missing required profile input: ' + name)
            rows.append(row)
            continue
        assessed = [assess(check, observation, artifacts, profile, as_of, sources) for observation in observations]
        # Multiple distinct target/scope rows cannot silently overwrite each other.
        # The site summary passes only when every declared observation is current;
        # a retained earlier failure is superseded solely by an explicit readback.
        latest = assessed[-1]
        unresolved_rows = []
        for previous in assessed[:-1]:
            previous_observation = previous['observations'][0]
            replaced = bool(previous['artifact_ids']) and any(
                item['verdict'] == 'pass' and item['freshness'] in ('current', 'dated')
                and previous['freshness'] != 'binding-mismatch'
                and not item['pending_readback']
                and item['observations'][0]['target'] == previous_observation['target']
                and item['observations'][0]['scope'] == previous_observation['scope']
                and item['observations'][0]['check_revision'] == previous_observation['check_revision']
                and item['observations'][0].get('source_config_binding', profile['source_config_binding']) == previous_observation.get('source_config_binding', profile['source_config_binding'])
                and item['population_ref'] == previous['population_ref']
                and item['context_id'] == previous['context_id']
                and not any(effect['status'] in ('UNKNOWN', 'possibly-sent') for effect in previous['preserved_effects'])
                and item['observations'][0].get('readback', {}).get('status') == 'observed-fixed'
                and set(previous['artifact_ids']).issubset(set(item['observations'][0]['readback'].get('original_artifact_ids', [])))
                for item in assessed if isinstance(item['observations'][0].get('readback'), dict))
            receipt_only = previous_observation.get('_retained_resolved') is True and not any(effect['status'] in ('UNKNOWN', 'possibly-sent') for effect in previous['preserved_effects'])
            if not replaced and previous['verdict'] != 'pass' and not receipt_only:
                unresolved_rows.append(previous)
        row = dict(latest)
        row['observations'] = observations
        row['scoped_results'] = [dict({key: item[key] for key in ('check_id', 'check_revision', 'scope', 'target', 'applicability', 'execution', 'verdict', 'freshness', 'artifact_ids', 'reasons', 'pending_readback', 'temporal_scope', 'population_ref', 'context_id', 'population_role', 'population_scope_kind')},
            retained_result=item['observations'][0].get('_retained_result')) for item in assessed]
        row['preserved_effects'] = [effect for item in assessed for effect in item['preserved_effects']]
        if unresolved_rows and latest['verdict'] != 'fail':
            row['verdict'] = 'unknown'
            if any(previous['applicability'] == 'applicable' for previous in unresolved_rows):
                row['applicability'] = 'applicable'
            row['reasons'] = ['Prior unresolved observation requires matching fix readback'] + row['reasons']
            row['pending_readback'] = True
        rows.append(row)
    return rows


def denominators(rows):
    return {'all_checks': len(rows), 'applicable': sum(row['applicability'] == 'applicable' for row in rows), 'not_applicable_with_reason': sum(row['applicability'] == 'not-applicable' and row['freshness'] == 'current' for row in rows), 'undetermined': sum(row['applicability'] == 'undetermined' for row in rows), 'current_evidenced': sum(row['freshness'] == 'current' and row['execution'] == 'completed' for row in rows), 'dated_evidenced': sum(row['freshness'] == 'dated' and row['execution'] == 'completed' for row in rows), 'failed': sum(row['verdict'] == 'fail' for row in rows), 'blocked': sum(row['execution'] == 'blocked' for row in rows), 'not_run': sum(row['execution'] == 'not-run' for row in rows), 'stale_or_mismatched': sum(row['freshness'] in ('stale', 'binding-mismatch') for row in rows), 'pending_readback': sum(row['pending_readback'] for row in rows), 'unresolved': len(missing_rows(rows))}


def missing_rows(rows):
    return [row for row in rows if row['freshness'] == 'dated' or row['verdict'] != 'pass' and not (row['applicability'] == 'not-applicable' and row['freshness'] == 'current')]


def markdown(site_id, rows, missing=False):
    body = ['# ' + ('Missing work' if missing else 'Findings') + ': ' + site_id, '', 'Offline validated evidence projection. A valid report is not SEO, deployment or traffic acceptance. Dated verdicts apply only to their recorded target/date/window and do not establish current state.', '', '| Check | Applicability | Execution | Verdict | Freshness | Recorded time / audit as of | Reason |', '| --- | --- | --- | --- | --- | --- | --- |']
    for row in missing_rows(rows) if missing else rows:
        reason = '; '.join(row['reasons']).replace('|', '\\|').replace('\n', ' ')
        temporal = row.get('temporal_scope', {})
        recorded = '; '.join(item['observed_at'] + ' (data: ' + item['data_as_of'] + ')' for item in temporal.get('artifacts', [])) or '-'
        recorded += '; audit as of: ' + (temporal.get('audit_as_of') or 'unobserved')
        body.append('| ' + ' | '.join([row['check_id'], row['applicability'], row['execution'], row['verdict'], row['freshness'], recorded, reason]) + ' |')
    return '\n'.join(body) + '\n'


def unchanged(inputs):
    require(all(sha(regular(path)) == expected for path, expected in inputs.items()), "Profile/registry/source/evidence input changed during import")


def current_pointer(profile_path):
    pointer_path = profile_path.parent / 'current-run.json'
    if not pointer_path.exists():
        return None, None
    pointer = load(pointer_path)
    require(isinstance(pointer, dict) and set(pointer) == {'run', 'run_sha256'}, 'current-run must contain only relative run and run_sha256')
    require(text(pointer['run']) and not Path(pointer['run']).is_absolute(), 'current-run locator must be relative')
    require(isinstance(pointer['run_sha256'], str) and HASH.fullmatch(pointer['run_sha256']), 'invalid current-run hash')
    return safe(profile_path.parent / pointer['run']), pointer['run_sha256']


def retained_evidence(run_path, run):
    filename = 'effective-evidence.json' if 'effective-evidence.json' in run['files'] else 'evidence.json'
    if filename not in run['files']:
        return {'observations': []}, {}
    evidence = load(run_path / filename)
    artifacts = {}
    for original in evidence['artifacts']:
        artifact = dict(original)
        artifact['resolved_path'] = next(item['path'] for item in run['artifacts'] if item['id'] == artifact['id'])
        artifact['_input_base'] = artifact.get('_input_base') or run.get('evidence_base') or str(run_path)
        artifact['_coverage_inputs'] = []
        if any(field in artifact['coverage'] for field in ('observed_members', 'observed_membership_manifest')):
            artifact['_observed_members'] = member_set(artifact['coverage'], 'observed_members',
                'observed_membership_manifest', artifact['_input_base'], artifact['_coverage_inputs'])
        artifacts[artifact['id']] = artifact
    return evidence, artifacts


def carry_history(profile_path, profile, evidence, artifacts, inputs):
    """Join only unresolved observations/effect receipts, never an aged former pass."""
    run_path, expected = current_pointer(profile_path)
    if run_path is None:
        return evidence, artifacts, []
    run = validate_run(run_path, expected)
    require(run['site_id'] == profile['site_id'], 'history pointer selects another site')
    inputs[profile_path.parent / 'current-run.json'] = sha(profile_path.parent / 'current-run.json')
    inputs[run_path / 'run.json'] = expected
    prior, prior_artifacts = retained_evidence(run_path, run)
    rows = {row['check_id']: row for row in load(run_path / 'checks.json')['checks']}
    old_checks = {check['id']: check for check in load(run_path / 'registry.json')['checks']}
    old_sources = {source['source_id']: source for source in source_rows(load(run_path / 'source-coverage.json'))}
    old_profile = load(run_path / 'profile.json')
    old_coverage = old_profile['coverage_policy'] if isinstance(old_profile['coverage_policy'], dict) else {}
    failed_checks = {item['check_id'] for item in prior.get('observations', []) if item['verdict'] == 'fail'}
    observations, used = [], set()
    for observation in prior.get('observations', []):
        row = rows.get(observation['check_id'], {})
        effects = any(prior_artifacts[item].get('effect_status') in ('UNKNOWN', 'possibly-sent', 'sent', 'completed') for item in observation['artifact_ids'])
        if effects or (row.get('verdict') == 'fail' or row.get('pending_readback')) and (observation['verdict'] == 'fail' or observation.get('readback') and observation['check_id'] not in failed_checks):
            # Preserve original selected binding across a later profile change.
            observation = dict(observation)
            observation.setdefault('source_config_binding', old_profile['source_config_binding'])
            observation.setdefault('_retained_check', old_checks[observation['check_id']])
            observation.setdefault('_retained_sources', {identity: old_sources[identity] for identity in old_checks[observation['check_id']]['upstream_source_ids']})
            observation.setdefault('_retained_policy', old_profile.get('assessment_policies', {}).get(observation.get('assessment_policy_id')))
            original_result = next((item for item in row.get('scoped_results', []) if item['artifact_ids'] == observation['artifact_ids'] and item['target'] == observation['target'] and item['scope'] == observation['scope']), row)
            observation.setdefault('_retained_result', {key: original_result.get(key) for key in ('verdict', 'freshness', 'temporal_scope', 'population_ref', 'context_id')})
            if observation['artifact_ids']:
                selected = prior_artifacts[observation['artifact_ids'][0]]['coverage']
                observation.setdefault('_retained_population', old_coverage.get('populations', {}).get(selected.get('population_ref')))
                observation.setdefault('_retained_context', old_coverage.get('contexts', {}).get(selected.get('context_id')))
            if effects and row.get('verdict') == 'pass' and not row.get('pending_readback'):
                observation.setdefault('_retained_resolved', True)
            observations.append(observation)
            used.update(observation['artifact_ids'])
            if isinstance(observation.get('readback'), dict):
                used.update(observation['readback'].get('original_artifact_ids', []))
                used.update(observation['readback'].get('artifact_ids', []))
    merged = dict(artifacts)
    for identity in used:
        artifact = prior_artifacts[identity]
        if identity in merged:
            clean = lambda item: {key: value for key, value in item.items() if not key.startswith('_') and key not in ('path', 'resolved_path')}
            require(clean(merged[identity]) == clean(artifact), 'artifact ID reused with different retained evidence: ' + identity)
        else:
            merged[identity] = artifact
    def comparison(observation):
        value = {key: item for key, item in observation.items() if not key.startswith('_retained_')}
        value.setdefault('source_config_binding', profile['source_config_binding'])
        return value
    observations.extend(observation for observation in evidence['observations'] if not any(comparison(observation) == comparison(previous) for previous in observations))
    return dict(evidence, observations=observations), merged, [{'path': str(run_path), 'run_sha256': expected}]


def persist_run(args, profile, registry, coverage, checks, sources, evidence, artifacts, as_of, registration, inputs):
    output = safe(args.out)
    history = []
    if not registration:
        evidence, artifacts, history = carry_history(args.profile, profile, evidence, artifacts, inputs)
    rows = matrix(checks, sources, evidence, artifacts, profile, as_of)
    dump(output / 'checks.json', {'schema_version': 1, 'site_id': profile['site_id'], 'checks': rows})
    (output / 'findings.md').write_text(markdown(profile['site_id'], rows), encoding='utf-8')
    (output / 'missing.md').write_text(markdown(profile['site_id'], rows, True), encoding='utf-8')
    unchanged(inputs)
    snapshots = {'profile.json': args.profile, 'registry.json': args.package / 'references/checks.json', 'source-coverage.json': args.package / 'references/source-coverage.json'}
    if not registration:
        snapshots['evidence.json'] = args.evidence
    for name, path in snapshots.items():
        with (output / name).open('xb') as handle:
            handle.write(regular(path).read_bytes())
    if not registration:
        effective_artifacts = [dict({key: value for key, value in artifact.items() if key != '_observed_members'}, path=artifact['resolved_path']) for artifact in artifacts.values()]
        dump(output / 'effective-evidence.json', {'observations': evidence['observations'], 'artifacts': effective_artifacts})
    handoffs = output / 'handoffs'; handoffs.mkdir()
    for kind in CLASSES:
        pending = []
        for row in missing_rows(rows):
            if row['kind'] != kind:
                continue
            check = checks[row['check_id']]
            pending.append({'check_id': row['check_id'], 'check_revision': row['check_revision'], 'target_allowlist': profile['allowed_targets'], 'inputs': check['inputs'], 'method': check['method'], 'acceptance': check['acceptance'], 'evidence_requirement': check['evidence_requirement'], 'source_provenance': check['source_provenance'], 'reasons': row['reasons'], 'preserved_effects': row['preserved_effects'], 'result_location': 'fresh evidence manifest for a fresh output directory'})
        dump(handoffs / (kind + '.json'), {'schema_version': 1, 'site_id': profile['site_id'], 'run_id': output.name, 'kind': kind, 'profile_sha256': sha(args.profile), 'profile_path': str(safe(args.profile)), 'registry_sha256': sha(args.package / 'references/checks.json'), 'source_coverage_sha256': sha(args.package / 'references/source-coverage.json'), 'source_config_binding': profile['source_config_binding'], 'source_selectors': profile['source_selectors'], 'input_locators': profile['input_locators'], 'account_property_locators': profile['account_property_locators'], 'no_replay': True, 'action_scope': profile['action_scope'], 'checks': pending})
    pointer = args.profile.parent / 'current-run.json'
    if not registration and pointer.exists():
        with (output / 'previous-current-run.json').open('xb') as handle:
            handle.write(regular(pointer).read_bytes())
    files = {path.relative_to(output).as_posix(): sha(path) for path in sorted(output.rglob('*')) if path.is_file()}
    run = {'schema_version': 1, 'status': 'registration-only' if registration else 'valid-import', 'site_id': profile['site_id'], 'run_id': output.name, 'profile_sha256': sha(args.profile), 'registry_version': registry['registry_version'], 'registry_sha256': sha(args.package / 'references/checks.json'), 'source_coverage_sha256': sha(args.package / 'references/source-coverage.json'), 'as_of': as_of.isoformat(), 'source_config_binding': profile['source_config_binding'], 'evidence_manifest_sha256': None if registration else sha(args.evidence), 'coverage_denominators': denominators(rows), 'limitations': ['Offline validation and projection only; native collection/expert execution must occur before import.', 'No SEO score, acquisition forecast, provider effect or automatic replay is produced.'], 'profile_base': str(safe(args.profile.parent)), 'evidence_base': None if registration else str(safe(args.evidence.parent)), 'population_inputs': profile.get('_coverage_inputs', []) + [item for artifact in artifacts.values() for item in artifact.get('_coverage_inputs', [])], 'applicability_inputs': evidence.get('_applicability_inputs', []), 'files': files, 'artifacts': [{'id': artifact['id'], 'path': artifact['resolved_path'], 'sha256': artifact['sha256']} for artifact in artifacts.values()]}
    run['history_runs'] = history
    unchanged(inputs)
    dump(output / 'run.json', run)
    # Verify complete immutable readback before publishing the sole mutable report pointer.
    validate_run(output)
    if not registration:
        unchanged(inputs)
        pointer_value = {'run': os.path.relpath(output, args.profile.parent), 'run_sha256': sha(output / 'run.json')}
        descriptor, name = tempfile.mkstemp(prefix='.current-run-', suffix='.json', dir=args.profile.parent)
        stage = Path(name)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                json.dump(pointer_value, handle, indent=2); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
            safe(pointer)
            os.replace(stage, pointer)
        finally:
            if stage.exists():
                stage.unlink()
    return {'status': run['status'], 'site_id': profile['site_id'], 'run': str(output), 'run_sha256': sha(output / 'run.json'), 'coverage_denominators': run['coverage_denominators'], 'acceptance': 'not implied by command success'}


def validate_run(output, expected_sha=None, ancestors=None):
    output = safe(output)
    ancestors = set() if ancestors is None else set(ancestors)
    require(str(output) not in ancestors, 'retained history cycle')
    ancestors.add(str(output))
    run_path = regular(output / 'run.json')
    if expected_sha is not None:
        require(sha(run_path) == expected_sha, 'current-run manifest hash mismatch')
    run = load(run_path)
    object_fields(run, ['schema_version', 'site_id', 'files', 'artifacts', 'as_of'], 'run manifest')
    require(isinstance(run['files'], dict) and isinstance(run['artifacts'], list), 'invalid run file inventory')
    for previous in run.get('history_runs', []):
        validated = validate_run(Path(previous['path']), previous['run_sha256'], ancestors)
        require(validated['site_id'] == run['site_id'], 'retained history site mismatch')
    for relative, expected in run['files'].items():
        path = safe(output / relative)
        require(output in path.parents, 'run file inventory escapes output')
        require(sha(regular(path)) == expected, 'immutable report file hash mismatch: ' + relative)
    for item in run.get('population_inputs', []) + run.get('applicability_inputs', []):
        require(sha(regular(item['path'])) == item['sha256'], 'retained population/input manifest hash mismatch')
    for artifact in run['artifacts']:
        require(sha(regular(artifact['path'])) == artifact['sha256'], 'retained artifact hash mismatch')
    for required in ('checks.json', 'profile.json', 'registry.json', 'source-coverage.json', 'findings.md', 'missing.md'):
        require(required in run['files'], 'run inventory omits required report: ' + required)
    return run


def report_site(profile_path, profile, registry, coverage, checks, sources, run_path=None, expected_sha=None):
    run = None
    as_of = datetime.now(timezone.utc)
    evidence, artifacts = {'observations': []}, {}
    if run_path is not None:
        run = validate_run(run_path, expected_sha)
        require(run['site_id'] == profile['site_id'], 'current-run points at another site')
        prepare_populations(profile, run.get('profile_base', str(profile_path.parent)) if profile_path.parent == run_path else profile_path.parent)
        rows = load(run_path / 'checks.json')['checks']
        require(isinstance(rows, list), 'invalid checks report')
        # Re-evaluate against current profile/registry from the retained evidence,
        # keeping old runs immutable and exposing newly introduced checks.
        if (run_path / 'evidence.json').exists():
            retained, artifacts = retained_evidence(run_path, run)
            evidence = {'observations': [observation for observation in retained['observations'] if observation['check_id'] in checks]}
        as_of = max(datetime.now(timezone.utc), when(run['as_of']))
        projected = matrix(checks, sources, evidence, artifacts, profile, as_of)
        profile_changed = run['profile_sha256'] != sha(profile_path)
        old_checks = {row['check_id']: row for row in rows}
        old_registry = {check['id']: check for check in load(run_path / 'registry.json')['checks']}
        old_sources = {source['source_id']: source for source in source_rows(load(run_path / 'source-coverage.json'))}
        for row in projected:
            old = old_checks.get(row['check_id'])
            if old is None:
                row['reasons'] = ['New current-registry check absent from retained report', *row['reasons']]
            elif old['check_revision'] != checks[row['check_id']]['revision'] or profile_changed or old_registry.get(row['check_id']) != checks[row['check_id']] or any(old_sources.get(source_id) != sources[source_id] for source_id in checks[row['check_id']]['upstream_source_ids']):
                row.update(verdict='unknown', freshness='binding-mismatch')
                row['reasons'] = ['Profile, check contract or selected source version changed since retained run', *row['reasons']]
        rows = projected
    else:
        rows = matrix(checks, sources, evidence, artifacts, profile, datetime.now(timezone.utc))
    return {'site_id': profile['site_id'], 'run': str(run_path) if run_path is not None else None, 'never_audited': run is None, 'as_of': as_of.isoformat(), 'checks': rows, 'coverage_denominators': denominators(rows)}


def missing(args):
    registry, coverage, checks, sources = package_data(args.package)
    if args.run is not None:
        run_path = safe(args.run)
        run = validate_run(run_path)
        profile_path = run_path / 'profile.json'
        # Snapshot filename is stable but its parent is a run, not an enrollment.
        profile = load(profile_path)
        result = report_site(profile_path, profile, registry, coverage, checks, sources, run_path)
        return {'status': 'valid-report', 'registry_version': registry['registry_version'], **result, 'acceptance': 'not implied by command success'}
    sites = safe(args.sites)
    require(sites.is_dir(), '--sites must be an existing directory')
    profiles = sorted(sites.glob('*/profile.json'))
    results, ids = [], set()
    for path in profiles:
        try:
            profile = profile_data(path)
            require(profile['site_id'] not in ids, 'duplicate enrolled site_id')
            ids.add(profile['site_id'])
            run_path, expected = current_pointer(path)
            results.append(dict(report_site(path, profile, registry, coverage, checks, sources, run_path, expected), status='valid-report'))
        except (OSError, ValueError, UnicodeError, TypeError, KeyError) as exc:
            rows = [dict(default_row(check, 'Enrollment error: ' + str(exc)), execution='error') for check in checks.values()]
            results.append({'site_id': path.parent.name, 'profile_path': str(path), 'status': 'error',
                'error': str(exc), 'never_audited': None, 'run': None, 'checks': rows,
                'coverage_denominators': denominators(rows)})
    errors = sum(result.get('status') == 'error' for result in results)
    return {'status': 'PARTIAL' if errors else 'valid-report', 'error_count': errors, 'registry_version': registry['registry_version'], 'site_count': len(results), 'sites': results, 'acceptance': 'not implied by command success'}


def run(args):
    if args.command == 'site-missing':
        return missing(args)
    output = safe(args.out)
    require(not output.exists(), 'immutable output already exists: ' + str(output))
    for input_path in [args.package, args.profile, *([args.evidence] if args.command == 'site-audit' else [])]:
        selected = safe(input_path)
        require(output != selected and output not in selected.parents and selected not in output.parents, 'output must not overlap package/profile/evidence input')
    output.mkdir(parents=True, exist_ok=False)
    try:
        input_paths = [args.profile, args.package / 'references/checks.json', args.package / 'references/source-coverage.json']
        if args.command == 'site-audit':
            input_paths.append(args.evidence)
        inputs = {path: sha(regular(path)) for path in input_paths}
        profile = profile_data(args.profile)
        registry, coverage, checks, sources = package_data(args.package)
        registration = args.command == 'site-add'
        as_of = datetime.now(timezone.utc) if registration else when(args.as_of)
        evidence, artifacts = ({'observations': []}, {}) if registration else evidence_data(args.evidence, profile, args.profile, registry, checks, as_of)
        for item in profile.get('_coverage_inputs', []) + [item for artifact in artifacts.values() for item in artifact.get('_coverage_inputs', [])] + evidence.get('_applicability_inputs', []):
            inputs[Path(item['path'])] = item['sha256']
        return persist_run(args, profile, registry, coverage, checks, sources, evidence, artifacts, as_of, registration, inputs)
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        error = output / 'import-error.json'
        if not error.exists():
            dump(error, {'schema_version': 1, 'status': 'invalid-import', 'error': str(exc), 'effects': 'none; no collector or replay is implemented'})
        raise ValueError(str(exc)) from None
