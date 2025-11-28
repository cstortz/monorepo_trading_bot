-- Production Partitioning Setup
-- Create monthly partitions for market_data table

-- Function to create monthly partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
        FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_date, end_date);
    
    -- Create indexes on the partition
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %I (symbol_id, timestamp DESC)',
        partition_name || '_symbol_timestamp_idx', partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %I (timestamp DESC)',
        partition_name || '_timestamp_idx', partition_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %I (time_frame, timestamp DESC)',
        partition_name || '_timeframe_timestamp_idx', partition_name);
END;
$$ LANGUAGE plpgsql;

-- Create partitions for the next 12 months
DO $$
DECLARE
    current_date DATE := date_trunc('month', CURRENT_DATE);
    i INTEGER;
BEGIN
    FOR i IN 0..11 LOOP
        PERFORM create_monthly_partition('market_data', current_date + (i || ' months')::INTERVAL);
    END LOOP;
END $$;
