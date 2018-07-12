import aws
import sc
import pandas as pd
aws.make_session()
def __main__():
    """ STEPPING """
    session = aws.make_session()
    res=aws.get('manifest').next_null('favs',session)
    assert res is not None

    uid = res[0][0]
    is_user = res[0][1]

    assert type(is_user) is bool
    assert type(uid) is int

    if is_user == True:
        print("type: USER")
        print(f"uid: {uid}")
        user(uid,session)
    if is_user == False:
        print("type: TRACK")
        print(f"uid: {uid}")
        track(uid,session)
    else:
        print("error")
    print('exiting.')

def user(uid,session):
    # api
    res = sc.Users.favorites(uid)
    pull = aws.favorites(res,uid)

    #preprocessing
    t = pull.tracks()
    f = pull.favs()
    t_man,f_man,u_man = pull.manifest()
    t_man
    u_man
    f_man
    #extraction

    session = aws.make_session()
    t_clean = aws.get('tracks').extract(t,session)
    f_clean = aws.get('favs').extract(f,session)

    t_clean
    aws.put('tracks').replace(t_clean,session)

    aws.put('favs').replace(f_clean,session)

    tman_c=aws.aws.clean(t_man)
    uman_c=aws.aws.clean(u_man)
    fman_c=aws.aws.clean(f_man)


    aws.put('manifest').replace(tman_c,session)
    aws.put('manifest').replace(fman_c,session)
    aws.put('manifest').replace(uman_c,session)

    #aws.get('manifest').all(session)
    #aws.get('manifest').next_null('favs',session)

    session.close()
    return 0

def track(uid,session):
    # api
    print("accessing api")
    res = sc.Tracks.favoriters(uid)
    pull = aws.favoriters(res,uid)

    #preprocessing
    print("preprocessing")
    f = pull.favs()
    u_man,t_man = pull.manifest()

    #extraction
    print("extraction")
    session = aws.make_session()

    f_clean = aws.get('favs').extract(f,session)

    print(f"putting f_clean {f_clean.shape[0]} into favs")
    aws.put('favs').replace(f_clean,session)


    uman_c = aws.aws.clean(u_man)
    tman_c = aws.aws.clean(t_man)

    print(f"putting u_man {uman_c.shape[0]}, t_man {tmac_c.shape[0]} into manifest")

    aws.put('manifest').replace(uman_c,session)
    aws.put('manifest').replace(tman_c,session)

    session.close()
    return 0

__main__()
