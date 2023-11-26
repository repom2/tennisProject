from vakio.models import WinShare, Combination


def find_lines():
    query = """
    select * from 
        (select *, 
            value / 100 as win, 
            round((prob*value*0.1)::numeric, 4) as yield
    from vakio_combination a 
    inner join vakio_winshare b on b.id=a.id) s 
    where yield > 1  order by yield desc
    """

    # https://github.com/VeikkausOy/sport-games-robot/blob/master/Python/robot.py