-- SQL script to create the favorites_favorite table
-- Run this in your PostgreSQL database if migrations fail

CREATE TABLE IF NOT EXISTS favorites_favorite (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    mgrp_code VARCHAR(30) NOT NULL,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT favorites_favorite_employee_id_fkey 
        FOREIGN KEY (employee_id) 
        REFERENCES "Employee_employee" (emp_id) 
        ON DELETE CASCADE,
    CONSTRAINT favorites_favorite_mgrp_code_fkey 
        FOREIGN KEY (mgrp_code) 
        REFERENCES "matgroups_matgroup" (mgrp_code) 
        ON DELETE CASCADE,
    CONSTRAINT favorites_favorite_employee_id_mgrp_code_unique 
        UNIQUE (employee_id, mgrp_code)
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS favorites_favorite_employee_id_idx ON favorites_favorite(employee_id);
CREATE INDEX IF NOT EXISTS favorites_favorite_mgrp_code_idx ON favorites_favorite(mgrp_code);
CREATE INDEX IF NOT EXISTS favorites_favorite_is_deleted_idx ON favorites_favorite(is_deleted);


