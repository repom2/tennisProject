
## Vakio id's are used to identify the different vakios in the database.

poetry run python manage.py vakio sports

## Calculate the vakio probabilities per line

poetry run python manage.py vakio prob

## Get the vakio win shares from veikkaus

poetry run python manage.py vakio winshares

## Bet on the vakio

poetry run python manage.py vakio find-lines

## Calculate the moniveto probabilities per score

poetry run python manage.py vakio moniveto

## Get win shares for moniveto

poetry run python manage.py vakio moniveto-winshares

select a.combination, m.value, a.value, a.value*0.01 * (b.prob * c.prob * d.prob * e.prob) as yield from vakio_monivetobet m
inner join vakio_monivetoodds a on a.combination=m.combination and a.moniveto_id=m.moniveto_id
and a.list_index=m.list_index
inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
inner join vakio_monivetoprob d on d.combination=a.match3 and d.moniveto_id = a.moniveto_id and d.list_index = a.list_index
inner join vakio_monivetoprob e on e.combination=a.match4 and e.moniveto_id = a.moniveto_id and e.list_index = a.list_index
where a.list_index=2 and a.moniveto_id=63271 
order by yield desc;
and m.bet=True 
and a.combination ilike '1-2,0-0,4-0,%';

select a.combination, m.value, a.value, a.value*0.01 * (b.prob * c.prob * d.prob) as yield from vakio_monivetobet m
inner join vakio_monivetoodds a on a.combination=m.combination and a.moniveto_id=m.moniveto_id
and a.list_index=m.list_index
inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
inner join vakio_monivetoprob d on d.combination=a.match3 and d.moniveto_id = a.moniveto_id and d.list_index = a.list_index
where a.list_index=2 and a.moniveto_id=63271
and m.bet=True
order by yield desc;

# Not bet
select a.combination, a.value, a.value, a.value*0.01 * (b.prob * c.prob * d.prob * e.prob) as yield from vakio_monivetoodds a
inner join vakio_monivetoprob b on b.combination=a.match1 and b.moniveto_id = a.moniveto_id and b.list_index = a.list_index
inner join vakio_monivetoprob c on c.combination=a.match2 and c.moniveto_id = a.moniveto_id and c.list_index = a.list_index
inner join vakio_monivetoprob d on d.combination=a.match3 and d.moniveto_id = a.moniveto_id and d.list_index = a.list_index
inner join vakio_monivetoprob e on e.combination=a.match3 and e.moniveto_id = a.moniveto_id and e.list_index = a.list_index
where a.list_index=2 and a.moniveto_id=63271 
and a.combination ilike '1-2,0-0,4-0,%'
order by yield desc;


select id, bets, prob, win, yield, ayield, combination, value, avalue from 
        (select a.id, b.bets, prob, bet, a.combination,
            b.value / 100 as win, 
            round((prob*(b.value*0.01/(0.1)))::numeric, 4) as yield,
            round((prob*(a.value*0.01/(0.1)))::numeric, 4) as ayield,
            b.value as value,
            a.value as avalue
    from vakio_combination a 
    inner join vakio_winshare b on b.combination=a.combination and 
        b.vakio_id = a.vakio_id and b.list_index = a.list_index
    where bet = True and a.vakio_id = 55513 and a.list_index = 2
    ) s  order by yield asc;


