from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    if not version:
        return

    # Check if part_number column exists in vehicle_part to avoid running this on fresh installs
    cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='vehicle_part' AND column_name='part_number'")
    if not cr.fetchone():
        return

    # 1. Create the new vehicle_part_specification table if it doesn't exist yet
    # Odoo hasn't created it yet during pre-migration
    cr.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_part_specification (
            id SERIAL PRIMARY KEY,
            name VARCHAR,
            group_id INTEGER,
            category_id INTEGER,
            create_uid INTEGER,
            create_date TIMESTAMP,
            write_uid INTEGER,
            write_date TIMESTAMP
        )
    """)

    # 2. Extract distinct specifications from vehicle_part
    # We will group by part_number, group_id, category_id
    cr.execute("""
        SELECT DISTINCT part_number, group_id, category_id
        FROM vehicle_part
        WHERE part_number IS NOT NULL
    """)
    specs = cr.fetchall()

    # 3. Insert into vehicle_part_specification and keep a map
    # A mapping from (part_number, group_id, category_id) to spec_id
    spec_map = {}
    for part_number, group_id, category_id in specs:
        cr.execute("""
            INSERT INTO vehicle_part_specification (name, group_id, category_id, create_uid, create_date, write_uid, write_date)
            VALUES (%s, %s, %s, 1, NOW(), 1, NOW())
            RETURNING id
        """, (part_number, group_id, category_id))
        spec_id = cr.fetchone()[0]
        spec_map[(part_number, group_id, category_id)] = spec_id

    # 4. Add specification_id to vehicle_part
    cr.execute("""
        ALTER TABLE vehicle_part ADD COLUMN IF NOT EXISTS specification_id INTEGER
    """)

    # 5. Update vehicle_part with the corresponding specification_id
    # Also we will build a mapping of old vehicle_part.id to spec_id for the M2M products
    cr.execute("""
        SELECT id, part_number, group_id, category_id FROM vehicle_part WHERE part_number IS NOT NULL
    """)
    parts = cr.fetchall()
    
    part_id_to_spec_id = {}
    for part_id, part_number, group_id, category_id in parts:
        spec_id = spec_map.get((part_number, group_id, category_id))
        if spec_id:
            cr.execute("UPDATE vehicle_part SET specification_id = %s WHERE id = %s", (spec_id, part_id))
            part_id_to_spec_id[part_id] = spec_id

    # 6. Migrate products many2many
    # The old table is vehicle_part_product_rel (part_id, product_id)
    # The new table is vehicle_part_spec_product_rel (spec_id, product_id)
    cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name='vehicle_part_product_rel'")
    if cr.fetchone():
        cr.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_part_spec_product_rel (
                spec_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                UNIQUE(spec_id, product_id)
            )
        """)
        cr.execute("SELECT part_id, product_id FROM vehicle_part_product_rel")
        product_rels = cr.fetchall()
        for part_id, product_id in product_rels:
            spec_id = part_id_to_spec_id.get(part_id)
            if spec_id:
                cr.execute("""
                    INSERT INTO vehicle_part_spec_product_rel (spec_id, product_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (spec_id, product_id))
