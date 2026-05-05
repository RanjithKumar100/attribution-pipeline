with sessions as (
    select * from {{ ref('stg_ga4__sessions') }}
),

-- assign channel based on source/medium
with_channel as (
    select
        user_pseudo_id,
        session_id,
        session_start_ts,
        session_end_ts,
        conversions,
        session_revenue,
        source,
        medium,
        campaign,

        case
            when lower(medium) = 'organic' then 'Organic Search'
            when lower(medium) = 'cpc' then 'Paid Search'
            when lower(medium) = 'email' then 'Email'
            when lower(medium) = 'referral' then 'Referral'
            when lower(medium) = 'social' then 'Social'
            when lower(source) = '(direct)' then 'Direct'
            else 'Other'
        end as channel,

        -- rank sessions per user by time (for first/last click)
        row_number() over (
            partition by user_pseudo_id
            order by session_start_ts asc
        ) as touch_number_asc,

        row_number() over (
            partition by user_pseudo_id
            order by session_start_ts desc
        ) as touch_number_desc,

        -- only count users who converted within 30-day lookback
        max(conversions) over (
            partition by user_pseudo_id
        ) as user_total_conversions

    from sessions
)

select * from with_channel