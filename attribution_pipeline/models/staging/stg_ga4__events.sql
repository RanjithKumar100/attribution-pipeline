with source as (
    select *
    from `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    where _TABLE_SUFFIX between '20210101' and '20211231'
),

renamed as (
    select
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,

        -- extract session id from event params
        (select value.int_value from unnest(event_params)
         where key = 'ga_session_id') as session_id,

        -- extract page location
        (select value.string_value from unnest(event_params)
         where key = 'page_location') as page_location,

        -- traffic source
        traffic_source.source as source,
        traffic_source.medium as medium,
        traffic_source.name as campaign,

        -- ecommerce revenue
        ecommerce.purchase_revenue as revenue

    from source
)

select * from renamed