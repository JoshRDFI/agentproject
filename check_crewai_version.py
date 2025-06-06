import pkg_resources
import inspect

try:
    version = pkg_resources.get_distribution('crewai').version
    print(f'CrewAI version: {version}')
    
    # Check for available modules
    import crewai
    print('\nAvailable modules in crewai:')
    for name in dir(crewai):
        if not name.startswith('_'):
            print(f'- {name}')
    
    # Check for available tools
    try:
        from crewai import tools
        print('\nAvailable tools in crewai.tools:')
        for name, obj in inspect.getmembers(tools):
            if not name.startswith('_'):
                print(f'- {name}')
                
        # Check for search tools
        try:
            from crewai.tools import search
            print('\nAvailable search tools:')
            for name, obj in inspect.getmembers(search):
                if not name.startswith('_'):
                    print(f'- {name}')
        except ImportError:
            print('\nNo separate search module found')
    except ImportError:
        print('\nNo tools module found')
        
except pkg_resources.DistributionNotFound:
    print('CrewAI is not installed')