with touchpoints as (
    select * from {{ ref('int_session_touchpoints') }}
),

last_click as (
    select
        user_pseudo_id,
        session_id,
        channel,
        source,
        medium,
        campaign,
        session_start_ts,
        session_revenue,
        'last_click' as attribution_model
    from touchpoints
    where touch_number_desc = 1
      and user_total_conversions > 0
)

select
    date(timestamp_micros(session_start_ts)) as attribution_date,
    channel,
    source,
    medium,
    attribution_model,
    count(distinct user_pseudo_id) as attributed_users,
    count(distinct session_id) as attributed_sessions,
    round(sum(session_revenue), 2) as attributed_revenue
from last_click
group by
    attribution_date,
    channel,
    source,
    medium,
    attribution_model
order by attribution_date desc