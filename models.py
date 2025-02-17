from extensions import db
from flask_login import UserMixin
from sqlalchemy import inspect, Column, Integer


def reflect_table(table_name):
    """Ensure the table exists and has a primary key before mapping it."""
    with db.engine.connect() as connection:
        inspector = inspect(connection)
        if table_name in inspector.get_table_names():
            db.Model.metadata.reflect(bind=db.engine)
            table = db.Model.metadata.tables.get(table_name, None)

            # 🔥 Ensure table has a primary key, else add one dynamically
            if table is not None and not any(c.primary_key for c in table.columns):
                table.append_column(Column('id', Integer, primary_key=True))  # Add 'id' as primary key
            print(f"Table {table_name} successfully reflected.")
            return table
        else:
            print(f"Table {table_name} not found in database.")
    return None  # Return None if the table is not found


### **🔹 Role-Based Access Control (RBAC) Models**
class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)

    role = db.relationship('Role', backref=db.backref('users', lazy=True))


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    table_name = db.Column(db.String(100), primary_key=True)
    can_read = db.Column(db.Boolean, default=False)
    can_write = db.Column(db.Boolean, default=False)
    can_update = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)

    role = db.relationship('Role', backref=db.backref('permissions', lazy=True))


### **🔹 Auto-Reflect FHIR Tables (Only If They Exist)**
def reflect_fhir_tables():
    """Explicitly reflect all tables before accessing them."""
    with db.engine.connect():
        db.Model.metadata.reflect(bind=db.engine)  # ✅ Ensure tables are loaded

        global Allergy, CarePlan, Claim, ClaimTransaction, Condition
        global Encounter, Immunization, Medication, Observation
        global Organization, Patient, Payer, PayerTransition, Procedure, Provider, Supply

        Allergy = type("Allergy", (db.Model,), {"__table__": reflect_table("allergies")})
        CarePlan = type("CarePlan", (db.Model,), {"__table__": reflect_table("careplans")})
        Claim = type("Claim", (db.Model,), {"__table__": reflect_table("claims")})
        ClaimTransaction = type("ClaimTransaction", (db.Model,), {"__table__": reflect_table("claims_transactions")})
        Condition = type("Condition", (db.Model,), {"__table__": reflect_table("conditions")})
        Encounter = type("Encounter", (db.Model,), {"__table__": reflect_table("encounters")})
        Immunization = type("Immunization", (db.Model,), {"__table__": reflect_table("immunizations")})
        Medication = type("Medication", (db.Model,), {"__table__": reflect_table("medications")})
        Observation = type("Observation", (db.Model,), {"__table__": reflect_table("observations")})
        Organization = type("Organization", (db.Model,), {"__table__": reflect_table("organizations")})
        Patient = type("Patient", (db.Model,), {"__table__": reflect_table("patients")})
        Payer = type("Payer", (db.Model,), {"__table__": reflect_table("payers")})
        PayerTransition = type("PayerTransition", (db.Model,), {"__table__": reflect_table("payer_transitions")})
        Procedure = type("Procedure", (db.Model,), {"__table__": reflect_table("procedures")})
        Provider = type("Provider", (db.Model,), {"__table__": reflect_table("providers")})
        Supply = type("Supply", (db.Model,), {"__table__": reflect_table("supplies")})

