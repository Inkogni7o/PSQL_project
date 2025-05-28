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

    -- Триггер для изменения следующей вакцинации при обновлении (используется с последней процедурой)
    CREATE OR REPLACE TRIGGER trg_update_visit_count
    AFTER INSERT ON Visits
    FOR EACH ROW
    EXECUTE FUNCTION update_visit_count();
                   
    CREATE OR REPLACE FUNCTION update_next_vaccination_date()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        -- Если изменилась дата вакцинации, обновляем дату следующей
        IF NEW.vaccination_date <> OLD.vaccination_date THEN
            NEW.next_vaccination_date := NEW.vaccination_date + INTERVAL '1 year';
        END IF;
        RETURN NEW;
    END;
    $$;

    CREATE TRIGGER trg_update_vaccination_date
    BEFORE UPDATE ON Vaccinations
    FOR EACH ROW
    EXECUTE FUNCTION update_next_vaccination_date();
    """) 


def insert_test_data(cursor) -> None:
    cursor.execute("""
    INSERT INTO Clinics (name, address, phone, website, opening_date, working_hours) VALUES
    ('Вета', 'г. Зеленоград, к315', '+7(904)568-90-71', 'vetaclinic-24.ru', '2010-05-15', '00:00-23:59'),
    ('Фунтик-Вет', 'г. Зеленоград, к330', '+7(499)110-95-00', 'funtik-vet.ru', '2015-03-10', '09:00-21:00'),
    ('Оригами', 'г. Зеленоград,  к322А', '+7(495)937-89-21', 'origami.vet', '2012-07-22', '00:00-23:59'),
    ('Поливет', 'г. Зеленоград, Панфиловский просп., 10', '+7(499)226-14-06', 'www.poli-vet.ru', '2018-01-30', '00:00-23:59'),
    ('Рядом', 'г. Зеленоград, Георгиевский просп., к2020', '+7(499)322-25-40', 'ryadomvet.ru', '2016-11-05', '00:00-23:59'),
    ('Динго', 'г. Зеленоград, к1455', '+7(495)504-55-35', 'dingovet.ru', '2014-09-18', '09:00-21:00'),
    ('Бис', 'г. Зеленоград, Фирсановское ш., вл. 1', '+7(977)180-41-47', '-', '2017-04-25', '09:00-18:00'),
    ('Астерион', 'г. Зеленоград, Георгиевский просп., 33, корп. 6', '+7(999)662-77-37', '-', '2013-02-14', '09:00-21:00'),
    ('Раденис', 'г. Зеленоград, ул. Андреевка, 31Б', '+7(495)542-60-11', 'vetradenis.ru', '2019-06-08', '09:00-21:00'),
    ('Кит', '4-й Мичуринский тупик, 5, микрорайон Сходня, Химки', '+7(495)120-40-90', 'vetkit.ru', '2011-12-03', '09:00-21:00');

    INSERT INTO Veterinarians (clinic_id, first_name, last_name, specialization, salary) VALUES
    (1, 'Елена', 'Полуянова', 'Терапевт', 75000.00),
    (1, 'Виктория', 'Родионова', 'Терапевт', 70000.00),
    (2, 'Алла', 'Поплавкова', 'Кардиолог', 80000.00),
    (3, 'Алексей', 'Ляшенко', 'Реаниматолог', 72000.00),
    (4, 'Алла', 'Филимонова', 'Хирург', 85000.00),
    (5, 'Сорокина', 'Светлана', 'Терапевт', 78000.00),
    (6, 'Игорь', 'Дорохов', 'Неврология', 82000.00),
    (9, 'Юрий', 'Юрьев', 'Терапевт', 76000.00),
    (10, 'Анастасия', 'Деменева', 'Офтальмолог', 83000.00),
    (10, 'Анастасия', 'Борщ', 'Терапевт', 77000.00);
    
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
                   
    INSERT INTO Pets (owner_id, name, species, breed, birth_date, gender, registration_date) VALUES
    (1, 'Барсик', 'Кошка', 'Британская', '2018-05-10', 'M', '2020-01-20'),
    (2, 'Шарик', 'Собака', 'Лабрадор', '2017-03-15', 'M', '2019-05-25'),
    (3, 'Мурка', 'Кошка', 'Дворовая', '2019-07-22', 'F', '2021-03-15'),
    (4, 'Рекс', 'Собака', 'Овчарка', '2016-11-05', 'M', '2018-07-10'),
    (5, 'Пушистик', 'Кошка', 'Персидская', '2020-01-30', 'F', '2020-11-17'),
    (6, 'Джек', 'Собака', 'Джек-рассел', '2018-09-18', 'M', '2019-09-23'),
    (7, 'Снежок', 'Кролик', 'Карликовый', '2019-04-25', 'M', '2021-03-01'),
    (8, 'Зефир', 'Хомяк', 'Сирийский', '2020-02-14', 'F', '2018-05-05'),
    (9, 'Рыжик', 'Кошка', 'Мейн-кун', '2017-06-08', 'M', '2020-06-13'),
    (10, 'Лайка', 'Собака', 'Хаски', '2019-12-03', 'F', '2019-12-08');
                   
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
                   
    INSERT INTO Vaccinations (pet_id, vet_id, vaccine_name, vaccination_date, next_vaccination_date, clinic_id) VALUES
    (1, 1, 'Nobivac Tricat', '2024-01-15', '2025-01-15', 1),
    (2, 3, 'Эурикан DHPPI2-LR', '2024-02-20', '2025-02-20', 2),
    (3, 4, 'Purevax RCPCh', '2024-03-25', '2025-03-25', 3),
    (4, 5, 'Вангард 7', '2024-04-10', '2025-04-10', 4),
    (5, 6, 'Фелоцел CVR', '2024-05-17', '2025-05-17', 5),
    (6, 7, 'Нобивак RL', '2024-06-23', '2025-06-23', 6),
    (7, 8, 'Раббивак-V', '2024-07-30', '2025-07-30', 7),
    (8, 9, 'Лейкоцел 2', '2024-08-05', '2025-08-05', 8),
    (9, 10, 'Дефенсор 3', '2024-09-13', '2025-09-13', 9),
    (10, 2, 'Мультифел-4', '2024-10-20', '2025-10-20', 1);
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


def create_procedurs(cursor) -> None:
    cursor.execute("""
    -- Процедура для регистрации нового животного
    CREATE OR REPLACE PROCEDURE register_new_pet(
        owner_first_name VARCHAR(50),
        owner_last_name VARCHAR(50),
        owner_phone VARCHAR(20),
        pet_name VARCHAR(50),
        pet_species VARCHAR(50),
        pet_breed VARCHAR(50),
        pet_birth_date DATE,
        pet_gender CHAR(1),
        pet_chip_number VARCHAR(20) DEFAULT NULL
    )
                   
    LANGUAGE plpgsql
    AS $$
    DECLARE
        owner_id_var INTEGER;
    BEGIN
        SELECT owner_id INTO owner_id_var 
        FROM Owners 
        WHERE phone = owner_phone;

        IF NOT FOUND THEN
            INSERT INTO Owners (first_name, last_name, phone)
            VALUES (owner_first_name, owner_last_name, owner_phone)
            RETURNING owner_id INTO owner_id_var;
        END IF;

        INSERT INTO Pets (owner_id, name, species, breed, birth_date, gender, chip_number)
        VALUES (owner_id_var, pet_name, pet_species, pet_breed, pet_birth_date, pet_gender, pet_chip_number);
        COMMIT;
                   
        RAISE NOTICE 'Питомец % успешно зарегистрирован для владельца % %', pet_name, owner_first_name, owner_last_name;
    END;
    $$;

                   
    -- Процедура записи на приём               
    CREATE OR REPLACE PROCEDURE schedule_visit(
        pet_id_param INTEGER,
        vet_id_param INTEGER,
        clinic_id_param INTEGER,
        visit_datetime TIMESTAMP,
        reason TEXT DEFAULT NULL
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        vet_available BOOLEAN;
    BEGIN
        SELECT NOT EXISTS (
            SELECT 1 FROM Visits 
            WHERE vet_id = vet_id_param 
              AND visit_date BETWEEN (visit_datetime - INTERVAL '30 minutes') 
                                AND (visit_datetime + INTERVAL '30 minutes')
        ) INTO vet_available;

        IF NOT vet_available THEN
            RAISE EXCEPTION 'Ветеринар занят в указанное время';
        END IF;

        INSERT INTO Visits (pet_id, vet_id, clinic_id, visit_date, status, diagnosis)
        VALUES (pet_id_param, vet_id_param, clinic_id_param, visit_datetime, 'scheduled', reason);
        COMMIT;
                   
        RAISE NOTICE 'Визит успешно запланирован на %', visit_datetime;
    END;
    $$;
                   
    -- Процедура рассчета дохода клиник
    CREATE OR REPLACE PROCEDURE calculate_clinic_revenue(
        clinic_id_param INTEGER,
        start_date DATE,
        end_date DATE,
        OUT total_revenue DECIMAL(10,2),
        OUT visit_count INTEGER
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        SELECT SUM(cost), COUNT(*) INTO total_revenue, visit_count
        FROM Visits
        WHERE clinic_id = clinic_id_param
          AND visit_date BETWEEN start_date AND end_date
          AND status = 'completed';

        IF total_revenue IS NULL THEN
            total_revenue := 0;
            visit_count := 0;
        END IF;

        RAISE NOTICE 'Клиника ID %: доход за период с % по % составляет % руб. (% визитов)',
            clinic_id_param, start_date, end_date, total_revenue, visit_count;
    END;
    $$;
                   
    -- Процедура генерации предупреждения о скорых прививках
    CREATE OR REPLACE PROCEDURE generate_vaccination_reminders(days_ahead INTEGER)
    LANGUAGE plpgsql
    AS $$
    DECLARE
        reminder RECORD;
    BEGIN
        RAISE NOTICE 'Напоминания о вакцинациях в ближайшие % дней:', days_ahead;

        FOR reminder IN
            SELECT p.name AS pet_name, o.first_name, o.last_name, o.phone, o.email,
                   v.vaccine_name, v.next_vaccination_date
            FROM Vaccinations v
            JOIN Pets p ON v.pet_id = p.pet_id
            JOIN Owners o ON p.owner_id = o.owner_id
            WHERE v.next_vaccination_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + days_ahead * INTERVAL '1 day')
            ORDER BY v.next_vaccination_date
        LOOP
            RAISE NOTICE 'Питомец: %, Владелец: % % (тел: %, email: %), Вакцина: %, Срок: %',
                reminder.pet_name, reminder.first_name, reminder.last_name, 
                reminder.phone, reminder.email, reminder.vaccine_name, 
                reminder.next_vaccination_date;
        END LOOP;
    END;
    $$;
                   
    -- Процедура передачи животного другому владельцу
    CREATE OR REPLACE PROCEDURE transfer_pet_to_another_owner(
    pet_id_param INTEGER,
    new_owner_first_name VARCHAR(50),
    new_owner_last_name VARCHAR(50),
    new_owner_phone VARCHAR(20)
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        new_owner_id_var INTEGER;
        old_owner_name TEXT;
        pet_name_var TEXT;
    BEGIN
        SELECT owner_id INTO new_owner_id_var 
        FROM Owners 
        WHERE phone = new_owner_phone;

        IF NOT FOUND THEN
            INSERT INTO Owners (first_name, last_name, phone)
            VALUES (new_owner_first_name, new_owner_last_name, new_owner_phone)
            RETURNING owner_id INTO new_owner_id_var;
        END IF;

        SELECT CONCAT(o.first_name, ' ', o.last_name), p.name 
        INTO old_owner_name, pet_name_var
        FROM Pets p
        JOIN Owners o ON p.owner_id = o.owner_id
        WHERE p.pet_id = pet_id_param;

        UPDATE Pets
        SET owner_id = new_owner_id_var
        WHERE pet_id = pet_id_param;

        COMMIT;
        RAISE NOTICE 'Питомец % передан от % к новому владельцу % %', 
            pet_name_var, old_owner_name, new_owner_first_name, new_owner_last_name;
    END;
    $$;
                   
    -- Процедура добавления новой вакцинации
    CREATE OR REPLACE PROCEDURE add_vaccination(
    pet_id_param INTEGER,
    vet_id_param INTEGER,
    vaccine_name_param VARCHAR(100),
    clinic_id_param INTEGER,
    batch_number_param VARCHAR(50) DEFAULT NULL
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        next_vacc_date DATE;
    BEGIN
        next_vacc_date := CURRENT_DATE + INTERVAL '1 year';

        INSERT INTO Vaccinations (pet_id, vet_id, vaccine_name, vaccination_date, 
                                 next_vaccination_date, batch_number, clinic_id)
        VALUES (pet_id_param, vet_id_param, vaccine_name_param, CURRENT_DATE, 
                next_vacc_date, batch_number_param, clinic_id_param);
        COMMIT;
        RAISE NOTICE 'Вакцинация % успешно добавлена для питомца ID %', vaccine_name_param, pet_id_param;
    END;
    $$;
    """)