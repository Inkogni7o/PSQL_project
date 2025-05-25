def create_all_tables(cursor) -> None:
    """Create all tabels in Clinics database"""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Clinics (
        clinic_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        address VARCHAR(200) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL UNIQUE,
        email VARCHAR(100),
        opening_date DATE NOT NULL CHECK (opening_date <= CURRENT_DATE),
        working_hours VARCHAR(50) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Veterinarians (
        vet_id SERIAL PRIMARY KEY,
        clinic_id INTEGER REFERENCES Clinics(clinic_id) ON DELETE CASCADE,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        specialization VARCHAR(100) NOT NULL,
        license_number VARCHAR(20) NOT NULL UNIQUE,
        hire_date DATE NOT NULL CHECK (hire_date <= CURRENT_DATE),
        salary DECIMAL(10,2) CHECK (salary > 0)
    );

    CREATE TABLE IF NOT EXISTS Owners (
        owner_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE,
        email VARCHAR(100),
        address VARCHAR(200),
        registration_date DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS Pets (
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

    CREATE TABLE IF NOT EXISTS Visits (
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

    CREATE TABLE IF NOT EXISTS Vaccinations (
        vaccination_id SERIAL PRIMARY KEY,
        pet_id INTEGER REFERENCES Pets(pet_id) ON DELETE CASCADE,
        vet_id INTEGER REFERENCES Veterinarians(vet_id) ON DELETE SET NULL,
        vaccine_name VARCHAR(100) NOT NULL,
        vaccination_date DATE NOT NULL DEFAULT CURRENT_DATE,
        next_vaccination_date DATE,
        batch_number VARCHAR(50),
        clinic_id INTEGER REFERENCES Clinics(clinic_id) ON DELETE SET NULL
    );
    """)


def create_trigger(cursor) -> None:
    cursor.execute("""
    CREATE OR REPLACE FUNCTION update_visit_count() RETURNS TRIGGER 
    LANGUAGE PLPGSQL
    AS 
    $$
    BEGIN
        UPDATE Visits
        SET total_visits_count = (
            SELECT COUNT(*) 
            FROM Visits 
            WHERE pet_id = NEW.pet_id
        )
        WHERE visit_id = NEW.visit_id;
        RETURN NEW;
    END;
    $$;

    CREATE OR REPLACE TRIGGER trg_update_visit_count
    AFTER INSERT ON Visits
    FOR EACH ROW
    EXECUTE FUNCTION update_visit_count();
    """) 


def insert_test_data(cursor) -> None:
    cursor.execute("""
    INSERT INTO Clinics (name, address, phone, email, opening_date, working_hours) VALUES
    ('Зеленоградский ВетЦентр', 'г. Зеленоград, ул. Центральная, 15', '+74951234567', 'vetcenter@mail.ru', '2010-05-15', '08:00-20:00'),
    ('Айболит', 'г. Зеленоград, пр. Ленинградский, 42', '+74957654321', 'aibolit@mail.ru', '2015-03-10', '09:00-21:00'),
    ('Доктор Вет', 'г. Зеленоград, ул. Солнечная, 7', '+74959876543', 'doctorvet@mail.ru', '2012-07-22', '08:00-19:00'),
    ('Лапки', 'г. Зеленоград, ул. Лесная, 33', '+74951231234', 'lapki@mail.ru', '2018-01-30', '10:00-18:00'),
    ('ВетЭкспресс', 'г. Зеленоград, ул. Панфиловцев, 12', '+74954564567', 'vetexpress@mail.ru', '2016-11-05', '07:00-23:00'),
    ('ЗооДоктор', 'г. Зеленоград, ул. Юности, 5', '+74953453456', 'zoodoctor@mail.ru', '2014-09-18', '08:00-20:00'),
    ('Кот и Пес', 'г. Зеленоград, ул. Гоголя, 20', '+74955675678', 'kotipes@mail.ru', '2017-04-25', '09:00-19:00'),
    ('ВетПомощь', 'г. Зеленоград, ул. Пушкина, 8', '+74956786789', 'vetpomosh@mail.ru', '2013-02-14', '08:00-22:00'),
    ('ЗооМед', 'г. Зеленоград, ул. Фестивальная, 3', '+74957897890', 'zoomed@mail.ru', '2019-06-08', '08:00-20:00'),
    ('ВетСервис', 'г. Зеленоград, ул. Школьная, 11', '+74958908901', 'vetservice@mail.ru', '2011-12-03', '09:00-21:00');

    INSERT INTO Veterinarians (clinic_id, first_name, last_name, specialization, license_number, hire_date, salary) VALUES
    (1, 'Иван', 'Петров', 'Хирургия', 'VET123456', '2015-06-10', 75000.00),
    (1, 'Елена', 'Смирнова', 'Терапия', 'VET654321', '2016-02-15', 70000.00),
    (2, 'Алексей', 'Иванов', 'Офтальмология', 'VET789012', '2017-03-20', 80000.00),
    (3, 'Ольга', 'Кузнецова', 'Дерматология', 'VET345678', '2018-05-12', 72000.00),
    (4, 'Дмитрий', 'Соколов', 'Кардиология', 'VET901234', '2019-07-08', 85000.00),
    (5, 'Мария', 'Попова', 'Онкология', 'VET567890', '2016-09-25', 78000.00),
    (6, 'Сергей', 'Лебедев', 'Неврология', 'VET123789', '2017-11-30', 82000.00),
    (7, 'Анна', 'Козлова', 'Стоматология', 'VET456123', '2018-04-05', 76000.00),
    (8, 'Андрей', 'Новиков', 'Ортопедия', 'VET789456', '2019-01-18', 83000.00),
    (9, 'Наталья', 'Морозова', 'Эндокринология', 'VET012345', '2020-08-22', 77000.00);
    
    INSERT INTO Owners (first_name, last_name, phone, email, address, registration_date) VALUES
    ('Александр', 'Волков', '+79161234567', 'volkov@mail.ru', 'г. Зеленоград, ул. Центральная, 10', '2020-01-15'),
    ('Екатерина', 'Зайцева', '+79162345678', 'zaytseva@mail.ru', 'г. Зеленоград, пр. Ленинградский, 25', '2019-05-20'),
    ('Михаил', 'Медведев', '+79163456789', 'medvedev@mail.ru', 'г. Зеленоград, ул. Солнечная, 5', '2021-03-10'),
    ('Ольга', 'Лисицына', '+79164567890', 'lisitsyna@mail.ru', 'г. Зеленоград, ул. Лесная, 12', '2018-07-05'),
    ('Денис', 'Соболев', '+79165678901', 'sobolev@mail.ru', 'г. Зеленоград, ул. Панфиловцев, 8', '2020-11-12'),
    ('Татьяна', 'Белова', '+79166789012', 'belova@mail.ru', 'г. Зеленоград, ул. Юности, 3', '2019-09-18'),
    ('Артем', 'Гусев', '+79167890123', 'gusev@mail.ru', 'г. Зеленоград, ул. Гоголя, 15', '2021-02-25'),
    ('Юлия', 'Воробьева', '+79168901234', 'vorobyeva@mail.ru', 'г. Зеленоград, ул. Пушкина, 6', '2018-04-30'),
    ('Павел', 'Орлов', '+79169012345', 'orlov@mail.ru', 'г. Зеленоград, ул. Фестивальная, 2', '2020-06-08'),
    ('Алина', 'Жукова', '+79160123456', 'zhukova@mail.ru', 'г. Зеленоград, ул. Школьная, 9', '2019-12-03');
                   
    INSERT INTO Pets (owner_id, name, species, breed, birth_date, gender, chip_number, registration_date) VALUES
    (1, 'Барсик', 'Кошка', 'Британская', '2018-05-10', 'M', 'CHIP123456', '2020-01-20'),
    (2, 'Шарик', 'Собака', 'Лабрадор', '2017-03-15', 'M', 'CHIP654321', '2019-05-25'),
    (3, 'Мурка', 'Кошка', 'Дворовая', '2019-07-22', 'F', 'CHIP789012', '2021-03-15'),
    (4, 'Рекс', 'Собака', 'Овчарка', '2016-11-05', 'M', 'CHIP345678', '2018-07-10'),
    (5, 'Пушистик', 'Кошка', 'Персидская', '2020-01-30', 'F', 'CHIP901234', '2020-11-17'),
    (6, 'Джек', 'Собака', 'Джек-рассел', '2018-09-18', 'M', 'CHIP567890', '2019-09-23'),
    (7, 'Снежок', 'Кролик', 'Карликовый', '2019-04-25', 'M', 'CHIP123789', '2021-03-01'),
    (8, 'Зефир', 'Хомяк', 'Сирийский', '2020-02-14', 'F', 'CHIP456123', '2018-05-05'),
    (9, 'Рыжик', 'Кошка', 'Мейн-кун', '2017-06-08', 'M', 'CHIP789456', '2020-06-13'),
    (10, 'Лайка', 'Собака', 'Хаски', '2019-12-03', 'F', 'CHIP012345', '2019-12-08');
                   
    INSERT INTO Visits (pet_id, vet_id, clinic_id, visit_date, diagnosis, treatment, cost, status) VALUES
    (1, 1, 1, '2025-01-10 10:00:00', 'Гастрит', 'Диета, лекарства', 2500.00, 'completed'),
    (2, 3, 2, '2025-02-15 11:30:00', 'Аллергия', 'Антигистаминные препараты', 1800.00, 'completed'),
    (3, 4, 3, '2025-03-20 09:15:00', 'Лишай', 'Противогрибковая мазь', 2200.00, 'completed'),
    (4, 5, 4, '2025-04-05 14:00:00', 'Перелом', 'Гипсовая повязка', 5000.00, 'completed'),
    (5, 6, 5, '2025-05-12 16:30:00', 'Конъюнктивит', 'Глазные капли', 1500.00, 'completed'),
    (6, 7, 6, '2025-06-18 12:45:00', 'Отит', 'Антибиотики, капли', 2000.00, 'completed'),
    (7, 8, 7, '2025-07-25 10:15:00', 'Кариес', 'Чистка, пломба', 3500.00, 'completed'),
    (8, 9, 8, '2025-08-30 15:00:00', 'Травма лапы', 'Перевязка', 1800.00, 'completed'),
    (9, 10, 9, '2025-09-08 11:30:00', 'Диабет', 'Инсулинотерапия', 4000.00, 'completed'),
    (10, 2, 1, '2025-10-15 13:45:00', 'Чумка', 'Интенсивная терапия', 6000.00, 'completed');
                   
    INSERT INTO Vaccinations (pet_id, vet_id, vaccine_name, vaccination_date, next_vaccination_date, batch_number, clinic_id) VALUES
    (1, 1, 'Nobivac Tricat', '2025-01-15', '2022-01-15', 'BATCH123', 1),
    (2, 3, 'Эурикан DHPPI2-LR', '2025-02-20', '2022-02-20', 'BATCH456', 2),
    (3, 4, 'Purevax RCPCh', '2025-03-25', '2022-03-25', 'BATCH789', 3),
    (4, 5, 'Вангард 7', '2025-04-10', '2022-04-10', 'BATCH012', 4),
    (5, 6, 'Фелоцел CVR', '2025-05-17', '2022-05-17', 'BATCH345', 5),
    (6, 7, 'Нобивак RL', '2025-06-23', '2022-06-23', 'BATCH678', 6),
    (7, 8, 'Раббивак-V', '2025-07-30', '2022-07-30', 'BATCH901', 7),
    (8, 9, 'Лейкоцел 2', '2025-08-05', '2022-08-05', 'BATCH234', 8),
    (9, 10, 'Дефенсор 3', '2025-09-13', '2022-09-13', 'BATCH567', 9),
    (10, 2, 'Мультифел-4', '2025-10-20', '2022-10-20', 'BATCH890', 1);
    """)

def create_indexes(cursor) -> None:
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_pets_owner_id ON Pets(owner_id);

    CREATE INDEX IF NOT EXISTS idx_visits_pet_id ON Visits(pet_id);
    CREATE INDEX IF NOT EXISTS idx_visits_vet_id ON Visits(vet_id);
    CREATE INDEX IF NOT EXISTS idx_visits_date ON Visits(visit_date);
    CREATE INDEX IF NOT EXISTS idx_visits_clinic_id ON Visits(clinic_id);

    CREATE INDEX IF NOT EXISTS idx_veterinarians_clinic_id ON Veterinarians(clinic_id);

    CREATE INDEX IF NOT EXISTS idx_vaccinations_pet_id ON Vaccinations(pet_id);
    CREATE INDEX IF NOT EXISTS idx_vaccinations_date ON Vaccinations(vaccination_date);
    """)