-- ============================================================
-- HBnB — Database Schema
-- ============================================================

-- User
CREATE TABLE IF NOT EXISTS users (
    id         CHAR(36)     PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name  VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    is_admin   BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Place
CREATE TABLE IF NOT EXISTS places (
    id          CHAR(36)       PRIMARY KEY,
    title       VARCHAR(255)   NOT NULL,
    description TEXT,
    price       DECIMAL(10, 2) NOT NULL,
    latitude    FLOAT          NOT NULL,
    longitude   FLOAT          NOT NULL,
    owner_id    CHAR(36)       NOT NULL,
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Amenity
CREATE TABLE IF NOT EXISTS amenities (
    id         CHAR(36)     PRIMARY KEY,
    name       VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Review
CREATE TABLE IF NOT EXISTS reviews (
    id         CHAR(36) PRIMARY KEY,
    text       TEXT     NOT NULL,
    rating     INT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    user_id    CHAR(36) NOT NULL,
    place_id   CHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    UNIQUE (user_id, place_id)
);

-- Place_Amenity (Many-to-Many)
CREATE TABLE IF NOT EXISTS place_amenity (
    place_id   CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id)   REFERENCES places(id)    ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);

-- Booking
CREATE TABLE IF NOT EXISTS bookings (
    id         CHAR(36)    PRIMARY KEY,
    place_id   CHAR(36)    NOT NULL,
    user_id    CHAR(36)    NOT NULL,
    check_in   DATE        NOT NULL,
    check_out  DATE        NOT NULL,
    guests     INT         NOT NULL DEFAULT 1,
    status     VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    CHECK (check_out > check_in),
    CHECK (guests >= 1),
    CHECK (status IN ('pending', 'confirmed', 'cancelled'))
);