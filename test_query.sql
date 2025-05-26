-- 1) клиники открытые после 2015
SELECT name, address, opening_date 
FROM Clinics 
WHERE opening_date > '2015-01-01' 
ORDER BY opening_date;

-- 2) работники с ЗП большей 75 тысяч
SELECT v.first_name, v.last_name, v.specialization, c.name AS clinic_name, v.salary
FROM Veterinarians v
JOIN Clinics c ON v.clinic_id = c.clinic_id
WHERE v.salary > 75000
ORDER BY v.salary;

-- 3) Количество животных по типу
SELECT species, COUNT(*) AS pet_count
FROM Pets
GROUP BY species
ORDER BY pet_count;

-- 4) средняя стоимость посещения
SELECT c.name, ROUND(AVG(v.cost), 2) AS "Средняя стоимость"
FROM Visits v
JOIN Clinics c ON v.clinic_id = c.clinic_id
GROUP BY c.name
ORDER BY 2;

-- 5) Вывести всех владельцев и их питомцев
SELECT o.first_name, o.last_name, p.name AS pet_name, p.species, p.breed
FROM Owners o
JOIN Pets p ON o.owner_id = p.owner_id
ORDER BY o.last_name, p.name;

-- 6) Вывести подробную информацию о посещениях клиник
SELECT p.name AS pet_name, o.first_name AS owner_name, 
       c.name AS clinic, vet.first_name AS vet_name,
       vi.visit_date, vi.diagnosis, vi.cost
FROM Visits vi
JOIN Pets p ON vi.pet_id = p.pet_id
JOIN Owners o ON p.owner_id = o.owner_id
JOIN Clinics c ON vi.clinic_id = c.clinic_id
JOIN Veterinarians vet ON vi.vet_id = vet.vet_id
ORDER BY vi.visit_date;

-- 7) Вывести кошек с вакциной, датирующаяся второй половиной 2021 года
SELECT p.name, p.breed, va.vaccine_name, va.vaccination_date
FROM Pets p
JOIN Vaccinations va ON p.pet_id = va.pet_id
WHERE p.species = 'Кошка' 
  AND va.vaccination_date >= '2021-06-01'
ORDER BY va.vaccination_date;

-- 8) Вывести посещения дороже 3000 р
SELECT p.name AS pet_name, vi.visit_date, vi.diagnosis, vi.cost
FROM Visits vi
JOIN Pets p ON vi.pet_id = p.pet_id
WHERE vi.cost > 3000
ORDER BY vi.cost;

-- 9) Вывести владельцев с 2 или более питомцами
SELECT o.first_name, o.last_name, 
       (SELECT COUNT(*) FROM Pets p WHERE p.owner_id = o.owner_id) AS pet_count
FROM Owners o
WHERE (SELECT COUNT(*) FROM Pets p WHERE p.owner_id = o.owner_id) > 1
ORDER BY pet_count DESC;

-- 10) Вывести ветеренаров без приемов в текущем месяце
SELECT v.first_name, v.last_name, v.specialization
FROM Veterinarians v
WHERE v.vet_id NOT IN (
    SELECT DISTINCT vet_id 
    FROM Visits 
    WHERE visit_date >= date_trunc('month', CURRENT_DATE)
);

-- 11) Вывести доходы клиник за последние 2 месяца
SELECT c.name, SUM(v.cost) AS total_income, COUNT(*) AS visit_count
FROM Visits v
JOIN Clinics c ON v.clinic_id = c.clinic_id
WHERE v.visit_date >= date_trunc('month', CURRENT_DATE - INTERVAL '2 month')
  AND v.visit_date < date_trunc('month', CURRENT_DATE)
GROUP BY c.name
ORDER BY total_income;

-- 12) Использованные вакцины по месяцам
SELECT EXTRACT(MONTH FROM vaccination_date) AS month,
COUNT(*) AS vaccination_count,
STRING_AGG(DISTINCT vaccine_name, ', ') AS vaccines_used
FROM Vaccinations
WHERE EXTRACT(YEAR FROM vaccination_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY month
ORDER BY month;

-- 13) Вывести питомцев с просроченной вакциной
WITH last_vaccinations AS (
    SELECT pet_id, MAX(next_vaccination_date) AS last_vaccination
    FROM Vaccinations
    GROUP BY pet_id
)
SELECT p.name, p.species, lv.last_vaccination
FROM Pets p
JOIN last_vaccinations lv ON p.pet_id = lv.pet_id
WHERE lv.last_vaccination < CURRENT_DATE;

--14) Вывести статистику по посещениям по дням недели
SELECT EXTRACT(DOW FROM visit_date) AS day_of_week,
       COUNT(*) AS visit_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Visits), 2) AS procent
FROM Visits
GROUP BY day_of_week
ORDER BY day_of_week;

-- 15) Вывести самые популярные диагнозы
SELECT diagnosis, COUNT(*) AS diagnosis_count
FROM Visits
WHERE diagnosis IS NOT NULL
GROUP BY diagnosis
ORDER BY diagnosis_count
LIMIT 5;

-- 16) Вывести статистику по ветеренарам, а именно количество приемов и доход 
SELECT v.first_name, v.last_name, v.specialization,
       COUNT(vi.visit_id) AS visit_count,
       SUM(vi.cost) AS total_income
FROM Veterinarians v
LEFT JOIN Visits vi ON v.vet_id = vi.vet_id
GROUP BY v.vet_id, v.first_name, v.last_name, v.specialization
ORDER BY visit_count;

-- 17) Вывести 5 клиентов, потративших больше всего средств
SELECT o.first_name, o.last_name,
       COUNT(vi.visit_id) AS visit_count,
       SUM(vi.cost) AS total_spent
FROM Owners o
JOIN Pets p ON o.owner_id = p.owner_id
JOIN Visits vi ON p.pet_id = vi.pet_id
GROUP BY o.owner_id
ORDER BY total_spent DESC
LIMIT 5;

-- 18) Вывести выручку по клининкам
SELECT c.name, 
       COUNT(DISTINCT v.vet_id) AS vet_count,
       COUNT(vi.visit_id) AS visit_count,
       SUM(vi.cost) AS total_income
FROM Clinics c
LEFT JOIN Veterinarians v ON c.clinic_id = v.clinic_id
LEFT JOIN Visits vi ON c.clinic_id = vi.clinic_id
GROUP BY c.name
ORDER BY total_income DESC;

-- 19) Представление со всей информацией о питомце
CREATE VIEW pet_history AS
SELECT p.pet_id, p.name AS pet_name, o.first_name AS owner_name, o.phone,
       vi.visit_date, vi.diagnosis, vi.treatment, vi.cost,
       va.vaccine_name, va.vaccination_date
FROM Pets p
JOIN Owners o ON p.owner_id = o.owner_id
LEFT JOIN Visits vi ON p.pet_id = vi.pet_id
LEFT JOIN Vaccinations va ON p.pet_id = va.pet_id;

-- 20) Мониторинг актиуальности вакцин
CREATE VIEW vaccination_monitoring AS
SELECT p.name AS pet_name, p.species, o.first_name AS owner_name, o.phone,
       v.vaccine_name, v.vaccination_date, v.next_vaccination_date,
       CASE WHEN v.next_vaccination_date < CURRENT_DATE THEN 'Просрочена'
            WHEN v.next_vaccination_date <= (CURRENT_DATE + INTERVAL '1 month') THEN 'Скоро'
            ELSE 'Актуальна' END AS status
FROM Vaccinations v
JOIN Pets p ON v.pet_id = p.pet_id
JOIN Owners o ON p.owner_id = o.owner_id;