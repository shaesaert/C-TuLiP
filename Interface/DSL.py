""""
Easy creation of variables
        X^(countx) ap <-> Xcountap   xsteps 


Implemented patterns
        [] p                        globally
        [](trig -> <> react)        Response 

"""

from tulip import spec


def Xtimes(ap, x=1, newap=None, owner='env'):
    """
    Create new variable which is true x time instances after ap is true.
    
    :param ap: string representing a simple boolean variable 
    :param x:
    :param newap: string representing name of a boolean variable 
    :param owner:  'sys' -> guarantee  or 'env'-> assume  (Default) +  placement of newap 
    :return:  GRSpec
    """
    env_vars, sys_vars, env_init, sys_init = set(), set(), set(), set()
    env_safe, sys_safe, env_prog, sys_prog = set(), set(), set(), set()

    if owner == 'env':
        old_var = ap
        for i in range(x-1):  # runs from  0..x-1
            next_var = 'X'+str(i+1)+ap
            env_vars |= {next_var}
            env_safe |= {next_var + ' <-> ' + '( X (' + old_var + '))'}
            old_var = next_var
        next_var = 'X' + str(x) + ap
        if newap:
            next_var = newap

        env_vars |= {next_var}
        env_safe |= {next_var + ' <-> ' + '( X (' + old_var + '))'}

    elif owner == 'sys':
        old_var = ap
        for i in range(x-1):  # runs from  0..x-1
            next_var = 'X'+str(i+1)+ap
            sys_vars |= {next_var}
            sys_safe |= {next_var + ' <-> ' + '( X (' + old_var + '))'}
            old_var = next_var
        next_var = 'X' + str(x) + ap
        sys_vars |= {next_var}
        sys_safe |= {next_var + ' <-> ' + '( X (' + old_var + '))'}

    print('Added variables ' + str(sys_vars | env_vars) )

    return spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                       env_safe, sys_safe, env_prog, sys_prog)




def globally(p='p', owner='env'):
    """
    response implements the LTL formula :
        [](p) 
    as a GR1specification
       && true 
       && [](p) 
       && []<> true
            
    :param p: 
    :param owner:  'sys' -> guarantee  or 'env'-> assume  (Default) +  placement of Aux 
    :return: GR1spec
    """
    env_vars, sys_vars, env_init, sys_init = set(), set(), set(), set()
    env_safe, sys_safe, env_prog, sys_prog = set(), set(), set(), set()

    if owner == 'env':
        env_vars = {}
        env_init = {}
        env_safe = {p}
        env_prog = set()
    elif owner == 'sys':
        sys_vars = {}
        sys_init = {}
        sys_safe = {p}
        sys_prog = set()

    print('Added globally:' + '[](' + p + ')')
    return spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                       env_safe, sys_safe, env_prog, sys_prog)


def response(trig='trig', react='act', owner='env', aux = 'aux'):
    """
    response implements the LTL formula :
        [](trig -> <> react) 
    as a GR1specification
       && aux 
       && [](X aux <-> (react || (aux && ! trig)) ) 
       && []<> aux
            
    :param trig:  Boolean formula
    :param react:  Boolean formula
    :param owner:  'sys' -> guarantee  or 'env'-> assume  (Default) +  placement of Aux 
    :return: GR1spec
    """

    env_vars, sys_vars, env_init, sys_init = set(), set(), set(), set()
    env_safe, sys_safe, env_prog, sys_prog = set(), set(), set(), set()

    if owner == 'env':
        env_vars = {aux}
        env_init = {aux}
        env_safe = {'(X ' + aux + ') <-> ( (' + react + ') ||' + '( ' + aux + ' && ! (' + trig + ') )' + ') '}
        env_prog = {aux}
    elif owner == 'sys':
        sys_vars = {aux}
        sys_init = {aux}
        sys_safe = {'(X '+ aux + ') <-> ( (' + react + ') ||' + '( ' + aux + ' && !(' + trig + ') ) ' + ')  '}
        sys_prog = {aux}

    print('Added global Response :' + '[](' + trig + '-> <>' + react + ')')
    return spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                       env_safe, sys_safe, env_prog, sys_prog)
