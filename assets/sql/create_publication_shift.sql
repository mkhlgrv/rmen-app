CREATE VIEW IF NOT EXISTS publication_shift(ticker, shift) AS
select
    val.ticker
     , case when var.freq = 'q' then
                    (12*cast(STRFTIME('%Y',julianday('now')) as int) + cast(STRFTIME('%m',julianday('now')) as int)
                        - 12*cast(STRFTIME('%Y',julianday(max(dt))) as int) - cast(STRFTIME('%m',julianday(max(dt))) as int))/3
            when var.freq = 'm' then
                            12*cast(STRFTIME('%Y',julianday('now')) as int) + cast(STRFTIME('%m',julianday('now')) as int)
                    - 12*cast(STRFTIME('%Y',julianday(max(dt))) as int) - cast(STRFTIME('%m',julianday(max(dt))) as int)
            when var.freq = 'w' then
                    cast(julianday('now', 'start of day') -
                         julianday(max(dt), 'start of day') as int )/7
            else julianday('now', 'start of day') - julianday(max(dt), 'start of day')
    end as shift
from
    value val
        inner join
    variable var
    on
            val.ticker = var.ticker
group by
    val.ticker