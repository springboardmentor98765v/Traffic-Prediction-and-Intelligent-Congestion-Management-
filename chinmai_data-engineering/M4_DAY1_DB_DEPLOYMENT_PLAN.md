# M4 Day 1 — Production Database Deployment Plan

## Owner

Intern 2 — Data Engineering & Traffic Monitoring

## Objective

Plan the production database setup, migration process, backup strategy,
and recovery approach for the Traffic Prediction and Intelligent
Congestion Management Platform.

---

## 1. Current Database

The project currently uses PostgreSQL for persistent traffic data.

The existing database contains traffic monitoring and analytics data.

Main tables include:

- roads
- traffic_readings
- traffic_history
- road_conditions
- hourly_traffic_metrics
- daily_traffic_metrics

Redis is used separately for caching and is not treated as the primary
persistent database.

---

## 2. Production Database Setup

The production environment should use a dedicated PostgreSQL instance.

Recommended setup:

- PostgreSQL 15+ or the project-approved PostgreSQL version
- Dedicated production database
- Dedicated application database user
- Strong database password
- Restricted network access
- Database connection through environment variables
- Regular monitoring of database health
- Connection pooling for API services

Production configuration should not contain credentials directly
inside source code.

Example environment variables:

POSTGRES_HOST=<production-db-host>
POSTGRES_PORT=5432
POSTGRES_DB=traffic_monitoring
POSTGRES_USER=<production-db-user>
POSTGRES_PASSWORD=<secure-production-password>

---

## 3. Database Migration Strategy

Database changes should be applied in a controlled order.

### Migration steps

1. Create the production PostgreSQL database.
2. Create the production database user.
3. Apply the base database schema.
4. Apply M2 schema changes.
5. Apply M3 analytics-related database changes.
6. Apply approved indexes.
7. Validate primary keys and foreign keys.
8. Validate constraints.
9. Load required reference data.
10. Verify record counts.
11. Run database/API regression tests.
12. Only then connect production application services.

Existing schema files and SQL migration files should be kept
version-controlled in the repository.

---

## 4. Migration Safety

Before applying a migration:

- Take a database backup.
- Test the migration in a staging environment.
- Verify the SQL before production execution.
- Apply one migration at a time.
- Record the migration version.
- Verify the database after migration.

Production migrations should not directly modify or delete existing
traffic data without approval.

---

## 5. Data Migration

Historical traffic data may be migrated from the existing environment
into production.

Important data includes:

- Historical traffic readings
- Road information
- Road conditions
- Hourly traffic metrics
- Daily traffic metrics

After migration, validate:

- Total record count
- Road count
- Duplicate records
- Missing records
- Timestamp validity
- Foreign-key relationships
- Index availability

Example validation:

Expected historical records:

4032

Expected monitored roads:

6

The final production counts should match the approved source dataset.

---

## 6. Backup Strategy

The production PostgreSQL database should use regular automated backups.

### Backup levels

#### Daily backup

Take a full database backup every day.

#### Weekly backup

Maintain a separate weekly backup for longer-term recovery.

#### Retention

Backups should be retained according to the team's approved
retention policy.

Recommended initial policy:

- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: according to project requirements

---

## 7. Backup Example

PostgreSQL logical backup can be created using:

pg_dump

Example:

pg_dump -h <host> -U <user> -d traffic_monitoring -F c -f traffic_monitoring_backup.dump

The backup file should be stored separately from the production
database.

---

## 8. Database Restore Strategy

If the production database is damaged or data is accidentally deleted:

1. Stop affected write operations if necessary.
2. Identify the latest valid backup.
3. Create/prepare a recovery database.
4. Restore the backup.
5. Validate the restored database.
6. Verify record counts and relationships.
7. Run application regression tests.
8. Redirect the application to the recovered database.
9. Monitor the application after recovery.

Restore testing should be performed periodically instead of assuming
that a backup is automatically recoverable.

---

## 9. Database Security

Production database security requirements:

- Do not commit `.env` files containing real credentials.
- Use strong database passwords.
- Use a dedicated application database user.
- Avoid using the PostgreSQL superuser for the application.
- Restrict database network access.
- Allow connections only from approved services.
- Use encrypted connections when required by the deployment environment.
- Rotate credentials according to team policy.

---

## 10. Indexes

Existing indexes should be reviewed before production deployment.

Important traffic query indexes include:

- road + timestamp
- sensor + timestamp
- road + congestion + timestamp

Analytics queries should also be monitored after deployment.

Indexes should be added based on measured production query patterns
rather than creating unnecessary indexes.

---

## 11. Production Validation Checklist

Before production sign-off:

- [ ] PostgreSQL production database created
- [ ] Production user created
- [ ] Environment variables configured
- [ ] Base schema applied
- [ ] M2 migrations applied
- [ ] M3 database changes applied
- [ ] Indexes verified
- [ ] Historical data validated
- [ ] Road-condition data validated
- [ ] Backup created
- [ ] Backup restore tested
- [ ] Database connectivity tested
- [ ] API regression tests passed
- [ ] No production credentials committed to Git

---

## 12. Rollback Plan

If a migration causes a production problem:

1. Stop the affected deployment.
2. Identify the migration that caused the issue.
3. Restore the previous database backup if required.
4. Validate database integrity.
5. Restore application compatibility.
6. Run regression tests.
7. Investigate and correct the migration in staging.
8. Retry production deployment only after approval.

---

## 13. M4 Handoff

The production database plan will support:

- Traffic Monitoring APIs
- Analytics APIs
- Alert integration
- AI Insights
- Frontend services
- Historical traffic analysis

All database schema changes should be coordinated with the dependent
teams before production deployment.

## Day 1 Deliverable

Production DB Deployment Plan completed.

Status:

Planning completed.

Production migration, backup execution, and restore testing will be
performed only in the approved deployment environment.