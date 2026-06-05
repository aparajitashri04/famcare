from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table: Many-to-many relationship between Service and Caregiver
service_caregiver_association = Table(
    'service_caregiver',
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.id'), primary_key=True),
    Column('caregiver_id', Integer, ForeignKey('caregivers.id'), primary_key=True),
)


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    duration_minutes = Column(Integer, nullable=False)  # 15, 30, 45, 60, etc.
    price = Column(Float, nullable=False)
    
    # Relationships
    bookings = relationship("Booking", back_populates="service")
    caregivers = relationship("Caregiver", secondary=service_caregiver_association, back_populates="services")
    
    def __repr__(self):
        return f"<Service id={self.id} name={self.name} duration={self.duration_minutes}min price={self.price}>"


class Caregiver(Base):
    __tablename__ = "caregivers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    specialization = Column(String)
    
    # Relationships
    bookings = relationship("Booking", back_populates="caregiver")
    services = relationship("Service", secondary=service_caregiver_association, back_populates="caregivers")
    
    def __repr__(self):
        return f"<Caregiver id={self.id} name={self.name}>"


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    contact = Column(String)
    
    # Relationships
    bookings = relationship("Booking", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient id={self.id} name={self.name}>"


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)  # Calculated: start_time + duration
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="bookings")
    caregiver = relationship("Caregiver", back_populates="bookings")
    patient = relationship("Patient", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking id={self.id} service={self.service_id} caregiver={self.caregiver_id} patient={self.patient_id} start={self.start_time}>"