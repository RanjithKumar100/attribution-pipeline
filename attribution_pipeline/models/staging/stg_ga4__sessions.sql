with events as (
    select * from {{ ref('stg_ga4__events') }}
),

sessions as (
    select
        user_pseudo_id,
        session_id,
        min(event_timestamp) as session_start_ts,
        max(event_timestamp) as session_end_ts,
        countif(event_name = 'purchase') as conversions,
        sum(coalesce(revenue, 0)) as session_revenue,
        any_value(source) as source,
        any_value(medium) as medium,
        any_value(campaign) as campaign
    from events
    where session_id is not null
    group by user_pseudo_id, session_id
)

select * from sessions