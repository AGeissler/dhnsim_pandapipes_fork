import pandapipes as pp
import json
from ..component_models.valve_control import CtrlValve
import pandapower.control as control

def export_network_components(net, path='', format=''):
    """
        Exports the network configurations via pandapipes default export 
        function (json_default) or by the network component files (json_readable).
    """
    # Default pandapipes json output
    if format == 'json_default':
        pp.to_json(net, path + 'network.json')

    # Readable component-wise json export
    elif format == 'json_readable':
        # Create components list from network (to avoid errors when specific
        # component not present!).
        components_dict = {}
        keylist = ['junction', 'pipe', 'heat_exchanger', 'circ_pump_mass',
                   'sink', 'source', 'valve', 'controller', 'external_grid']
        for key in keylist:
            if hasattr(net, key):
                components_dict[key+('' if key == 'circ_pump_mass' else 's')]=getattr(net, key)

        # Create new network.json file
        for component in components_dict:

            # Setup customized json export for controller components
            if component == 'controllers':
                json_object = [c.to_json() for c in components_dict.get(component)['object']]

            # Default df export for other components
            else:
                json_string = components_dict.get(component).to_json(orient='records')
                json_object = json.loads(json_string)

            # Write json to file
            with open(path + component + '.json', "w") as fout:
                json.dump(json_object, fout, indent=4, sort_keys=True)


def import_network_components(net, format='json_default', path=''):
    """
        Imports the network configurations via pandapipes default import 
        function (json_default) or by the network component files (json_readable).
    """
    # Default pandapipes json import
    if format == 'json_default':
        # Default pandapipes json output
        net = pp.from_json(path + 'network.json')

    # Component-wise import from Readable json files
    elif format == 'json_readable':
        # TODO: Add 'file exists' check to all of the import functions!
        # import components
        _import_junctions_to(net, path)
        _import_pipes_to(net, path)
        _import_sinks_to(net, path)
        #_import_sources_to(net, path)
        #_import_valves_to(net, path)
        #_import_external_grids_to(net, path)
        _import_heat_exchangers_to(net, path)
        _import_controllers_to(net, path)
        _import_pumps_to(net, path)  # TODO: Import inline pumps (check support of pandapipes)

    return net

def _read_component_file(path, fnam):
    # Code outline from: FHNW GPT Buddy, February 15th, 2024 at 15:05
    # Load JSON from file
    try:
        with open(path+fnam, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No file '{fnam}' found.")
    except IOError:
        print(f"An IO error occurred reading '{fnam}'.")
    except Exception as e:
        print(f"An unexpected error occurred trying to read '{fnam}': ", str(e))
    return None

def _import_heat_exchangers_to(net, path):
    """
        Import all heat exchanger components from import file (json_readable).
    """
    # Load JSON from file.
    heat_exchangers = _read_component_file(path, 'heat_exchangers.json')
    
    # add heat exchangers to pandapipes network
    if heat_exchangers:
        for hex in heat_exchangers:
            pp.create_heat_exchanger(net,
                                     diameter_m=hex.get('diameter_m'),
                                     from_junction=hex.get('from_junction'),
                                     in_service=hex.get('in_service'),
                                     loss_coefficient=hex.get('loss_coefficient'),
                                     name=hex.get('name'),
                                     qext_w=hex.get('qext_w'),
                                     to_junction=hex.get('to_junction'),
                                     type='heat_exchanger')

    return heat_exchangers

def _import_junctions_to(net, path):
    """
        Import all junction components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'junctions.json')
    junctions = json.load(f)

    # add junctions to pandapipes network
    for j in junctions:
        pp.create_junction(net, height_m=j.get('height_m'),
                           pn_bar=j.get('pn_bar'),
                           tfluid_k=j.get('tfluid_k'),
                           name=j.get('name'),
                           in_service=j.get('in_service'),
                           type='junction',
                           geodata=j.get('geodata'))

    return junctions

def _import_pipes_to(net, path):
    """
        Import all pipe components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'pipes.json')
    pipes = json.load(f)

    # add pipes to pandapipes network
    for p in pipes:
        pp.create_pipe_from_parameters(net,
                                       from_junction=p.get('from_junction'),
                                       to_junction=p.get('to_junction'),
                                       length_km=p.get('length_km'),
                                       diameter_m=p.get('diameter_m'),
                                       k_mm=p.get('k_mm'),
                                       loss_coefficient=p.get('loss_coefficient'),
                                       sections=p.get('sections'),
                                       alpha_w_per_m2k=p.get('alpha_w_per_m2k'),
                                       text_k=p.get('text_k'),
                                       qext_w=p.get('qext_w'),
                                       name=p.get('name'),
                                       geodata=None,
                                       in_service=p.get('in_service'),
                                       type=p.get('type'))

    return pipes


def _import_sinks_to(net, path):
    """
        Import all sink components from import file (json_readable).
    """
    # Load JSON from file
    sinks = _read_component_file(path, 'sinks.json')

    # add sinks to pandapipes network
    if sinks:
        for s in sinks:
            pp.create_sink(net,
                           junction=s.get('junction'),
                           mdot_kg_per_s=s.get('mdot_kg_per_s'),
                           scaling=s.get('scaling'),
                           name=s.get('name'),
                           in_service=s.get('in_service'),
                           type='sink')

    return sinks

def _import_sources_to(net, path):
    """
        Import all source components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'sources.json')
    sources = json.load(f)

    # add sources to pandapipes network
    for s in sources:
        pp.create_source(net,
                       junction=s.get('junction'),
                       mdot_kg_per_s=s.get('mdot_kg_per_s'),
                       scaling=s.get('scaling'),
                       name=s.get('name'),
                       in_service=s.get('in_service'),
                       type='source')

    return sources

def _import_valves_to(net, path):
    """
        Import all valve components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'valves.json')
    valves = json.load(f)

    # add valves to pandapipes network
    for v in valves:
        pp.create_valve(net,
                        from_junction=v.get('from_junction'),
                        to_junction=v.get('to_junction'),
                        diameter_m=v.get('diameter_m'),
                        opened=v.get('opened'),
                        loss_coefficient=v.get('loss_coefficient'),
                        name=v.get('name'),
                        type='valve')

    return valves

def _import_controllers_to(net, path):
    """
        Import all controller components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path + 'controllers.json')
    controllers = json.load(f)

    # add controllers to pandapipes network
    for c in controllers:
        if c.get('type') == 'CtrlValve':
            # create supply flow control
            CtrlValve(net=net,
                      in_service=c.get('in_service'),
                      initial_run=c.get('initial_run'),
                      level=c.get('level'),
                      order=c.get('order'),
                      data_source=c.get('object').get('data_source'),
                      profile_name=c.get('object').get('profile_name'),
                      valve_id=c.get('object').get('valve_id'),
                      mdot_set_kg_per_s=c.get('object').get('mdot_set_kg_per_s'),
                      gain=c.get('object').get('gain'),
                      tol=c.get('object').get('tol'),
                      name=c.get('name')
                      )

        elif c.get('type') == 'ConstControl':
            control.ConstControl(net=net,
                                 in_service=c.get('in_service'),
                                 initial_run=c.get('initial_run'),
                                 level=c.get('level'),
                                 order=c.get('order'),
                                 profile_name=c.get('object').get('profile_name'),
                                 data_source=c.get('object').get('data_source'),
                                 element=c.get('element'),
                                 variable=c.get('variable'),
                                 element_index=c.get('element_index'),
                                 )

    return controllers

def _import_external_grids_to(net, path):
    """
        Import all external grid components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'ext_grids.json')
    ext_grids = json.load(f)

    # add external grids to pandapipes network
    for g in ext_grids:
        pp.create_ext_grid(net,
                           junction=g.get('junction'),
                           p_bar=g.get('p_bar'),
                           t_k=g.get('t_k'),
                           name=g.get('name'),
                           in_service=g.get('in_service'),
                           type=g.get('type'))

    return ext_grids

def _import_pumps_to(net, path):
    """
        Import all pump components from import file (json_readable).
    """
    # Load JSON from file
    f = open(path+'circ_pump_mass.json')
    circ_pump_mass = json.load(f)

    # add pumps to pandapipes network
    for g in circ_pump_mass:
        pp.create_circ_pump_const_mass_flow(net,
                                            return_junction   = g.get('return_junction'),
                                            flow_junction     = g.get('flow_junction'),
                                            name              = g.get('name'),
                                            p_flow_bar        = g.get('p_flow_bar'),
                                            mdot_flow_kg_per_s= g.get('mdot_flow_kg_per_s'),
                                            t_flow_k          = g.get('t_flow_k'),
                                            type='pt')

    return circ_pump_mass
