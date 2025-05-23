import psycopg2

def create_all_tables(cursor):
    """Create all tabels in Clinics database"""
    cursor.execute("""-- Создание таблицы Clinics (Клиники)
CREATE TABLE Clinics (
    clinic_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    opening_date DATE NOT NULL CHECK (opening_date <= CURRENT_DATE),
    working_hours VARCHAR(50) NOT NULL
);

-- Создание таблицы Veterinarians (Ветеринары)
CREATE TABLE Veterinarians (
    vet_id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES Clinics(clinic_id) ON DELETE CASCADE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    license_number VARCHAR(20) NOT NULL UNIQUE,
    hire_date DATE NOT NULL CHECK (hire_date <= CURRENT_DATE),
    salary DECIMAL(10,2) CHECK (salary > 0)
);

-- Создание таблицы Owners (Владельцы)
CREATE TABLE Owners (
    owner_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    address VARCHAR(200),
    registration_date DATE DEFAULT CURRENT_DATE
);

-- Создание таблицы Pets (Питомцы)
CREATE TABLE Pets (
    pet_id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES Owners(owner_id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(50),
    birth_date DATE CHECK (birth_date <= CURRENT_DATE),
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    chip_number VARCHAR(20) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE
);

-- Создание таблицы Visits (Визиты)
CREATE TABLE Visits (
    visit_id SERIAL PRIMARY KEY,
    pet_id INTEGER REFERENCES Pets(pet_id) ON DELETE CASCADE,
    vet_id INTEGER REFERENCES Veterinarians(vet_id) ON DELETE SET NULL,
    clinic_id INTEGER REFERENCES Clinics(clinic_id) ON DELETE SET NULL,
    visit_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    diagnosis TEXT,
    treatment TEXT,
    cost DECIMAL(10,2) CHECK (cost >= 0),
    status VARCHAR(20) CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    total_visits_count INTEGER DEFAULT 0
);

-- Создание таблицы Vaccinations (Вакцинации)
CREATE TABLE Vaccinations (
    vaccination_id SERIAL PRIMARY KEY,
    pet_id INTEGER REFERENCES Pets(pet_id) ON DELETE CASCADE,
    vet_id INTEGER REFERENCES Veterinarians(vet_id) ON DELETE SET NULL,
    vaccine_name VARCHAR(100) NOT NULL,
    vaccination_date DATE NOT NULL DEFAULT CURRENT_DATE,
    next_vaccination_date DATE,
    batch_number VARCHAR(50),
    clinic_id INTEGER REFERENCES Clinics(clinic_id) ON DELETE SET NULL
);""")