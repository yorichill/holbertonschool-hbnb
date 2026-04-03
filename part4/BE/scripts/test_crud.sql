-- ============================================================
-- HBnB — Test CRUD Operations
-- ============================================================

-- SELECT vérification données initiales
SELECT id, first_name, last_name, email, is_admin FROM users;
SELECT id, name FROM amenities;

-- INSERT test place
INSERT INTO places (id, title, description, price, latitude, longitude, owner_id)
VALUES (
    'd4e5f6a7-b8c9-0123-defa-234567890123',
    'Test Place',
    'A test place',
    99.99,
    48.8566,
    2.3522,
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1'
);

-- INSERT test review
INSERT INTO reviews (id, text, rating, user_id, place_id)
VALUES (
    'e5f6a7b8-c9d0-1234-efab-345678901234',
    'Great place!',
    5,
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'd4e5f6a7-b8c9-0123-defa-234567890123'
);

-- INSERT place_amenity
INSERT INTO place_amenity (place_id, amenity_id) VALUES
    ('d4e5f6a7-b8c9-0123-defa-234567890123', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
    ('d4e5f6a7-b8c9-0123-defa-234567890123', 'b2c3d4e5-f6a7-8901-bcde-f12345678901');

-- INSERT test booking
INSERT INTO bookings (id, place_id, user_id, check_in, check_out, guests, status)
VALUES (
    'f6a7b8c9-d0e1-2345-fabc-456789012345',
    'd4e5f6a7-b8c9-0123-defa-234567890123',
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    '2026-06-01',
    '2026-06-05',
    2,
    'pending'
);

-- UPDATE
UPDATE places SET price = 149.99
WHERE id = 'd4e5f6a7-b8c9-0123-defa-234567890123';

UPDATE bookings SET status = 'confirmed'
WHERE id = 'f6a7b8c9-d0e1-2345-fabc-456789012345';

-- Vérification contrainte UNIQUE review (ce INSERT doit échouer)
-- INSERT INTO reviews (id, text, rating, user_id, place_id)
-- VALUES ('test-fail', 'Double review', 4,
--         '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
--         'd4e5f6a7-b8c9-0123-defa-234567890123');

-- DELETE
DELETE FROM bookings WHERE id = 'f6a7b8c9-d0e1-2345-fabc-456789012345';
DELETE FROM reviews  WHERE id = 'e5f6a7b8-c9d0-1234-efab-345678901234';
DELETE FROM places   WHERE id = 'd4e5f6a7-b8c9-0123-defa-234567890123';

-- Vérification finale
SELECT 'users'        AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'places',       COUNT(*) FROM places
UNION ALL
SELECT 'reviews',      COUNT(*) FROM reviews
UNION ALL
SELECT 'amenities',    COUNT(*) FROM amenities
UNION ALL
SELECT 'place_amenity',COUNT(*) FROM place_amenity
UNION ALL
SELECT 'bookings',     COUNT(*) FROM bookings;
