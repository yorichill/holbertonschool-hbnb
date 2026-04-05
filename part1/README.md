# HBnB Technical Documentation — Comprehensive Guide

Welcome to the **HBnB Technical Documentation**, a complete blueprint for the HBnB project.  
This document compiles **all diagrams, architecture notes, and API flows** to serve as a reference for developers and beginners alike.

---

## 📑 Table of Contents

1. [Introduction](#introduction)  
2. [High-Level Architecture](#high-level-architecture)  
3. [Business Logic Layer](#business-logic-layer)  
4. [API Interaction Flow](#api-interaction-flow)  
   - [User Management](#user-management)  
   - [Place Management](#place-management)  
   - [Booking Management](#booking-management)  
   - [Review Management](#review-management)  
   - [Payment Management](#payment-management)  
   - [Amenity Management](#amenity-management)  
   - [Admin Management](#admin-management)  
   - [Message Management](#message-management)  
5. [Tips](#tips)  

---

## Introduction

**Objective:**  
This document is a **technical blueprint** of the HBnB project. It combines high-level architecture, detailed class diagrams, and API flow explanations into a single, organized reference.  

**Scope:**  
- Serve as a guide for implementation.  
- Clarify how data moves through the layers.  
- Explain roles and responsibilities of components.  
- Include beginner-friendly notes and tips.

---

## High-Level Architecture

**Diagram Overview:**  
- **Presentation Layer** → Receives user requests and forwards them to BL (Facade Pattern).  
- **Business Logic Layer (BL)** → Applies rules, validates data, and prepares objects for persistence.  
- **Persistence Layer (Repo)** → Handles CRUD operations to the database.  
- **Database (MySQL)** → Physical storage of all application data.

**Design Notes:**  
- Facade Pattern simplifies interactions between API and BL.  
- BL does not interact directly with the database; all access goes through Repos.  
- Separation of concerns ensures maintainability and scalability.  

**Mermaid Diagram Snippet:**
```mermaid
classDiagram
    PresentationLayer --> BusinessLogicLayer : Facade Pattern
    BusinessLogicLayer --> PersistenceLayer : Database Operations
    PersistenceLayer --> MySQL : SQL Access
```

# Business Logic Layer (BLL)

## 🎯 Purpose
Contains all **business rules** and **application logic** of the system.

---

## 📦 Main Entities

| Entity   | Responsibilities |
|----------|-----------------|
| **User**     | Registration, authentication, profile updates |
| **Place**    | Create/update/search places, link amenities |
| **Booking**  | Create/cancel booking, check availability, calculate total price |
| **Review**   | Validate and post reviews, update ratings |
| **Payment**  | Process payments and refunds |
| **Amenity**  | Manage amenities and link to places |
| **Admin**    | Manage users and permissions |
| **Message**  | Manage conversations |

---

## 🧱 Design Principles

- ✅ **Validation before persistence**: All incoming data is validated in the business layer before saving.
- 🔁 **Alternative paths & loops**: Handles conditional flows (e.g., booking available vs unavailable).
- 🧪 **BL / Repositories separation**: Ensures code testability and maintainability.

---

## 🔗 Mermaid Diagram (Excerpt)

```mermaid
classDiagram
    class User {
        +register()
        +authenticate()
        +updateProfile()
    }
    class Place {
        +create()
        +update()
        +search()
        +linkAmenity()
    }
    class Booking {
        +create()
        +cancel()
        +checkAvailability()
        +calculateTotal()
    }
    class Review {
        +post()
        +update()
        +report()
    }
    class Payment {
        +process()
        +refund()
    }
    class Amenity {
        +create()
        +linkToPlace()
    }
    class Admin {
        +manageUsers()
        +managePermissions()
    }
    class Message {
        +send()
        +receive()
        +trackReadStatus()
    }
```

## API Interaction Flow

Each module below describes API calls, their path through the Business Layer (BL) and repositories, and alternative paths.  
This document helps visualize how requests move through the system and how errors or loops are handled.

---

## 👤 User Management

**Role:** Registration, profile management, authentication.

### Nominal Flow
User → API → BL validates → Repository saves → BL returns → API responds

### Alternatives
- ❌ Validation fails → `400 Bad Request`
- ✅ Success → `201 Created`

### Loop
- Multiple GET requests allowed to list users

---

## 🏠 Place Management

**Role:** Create, update, search, delete places; link amenities.

### Nominal Flow
User → API → BL validates → Repository saves/retrieves → BL returns → API responds

### Alternatives
- 🚫 Place unavailable
- ⚠️ Validation fails

### Loop
- Multiple search queries → returns array of results

---

## 📅 Booking Management

**Role:** Book a place, cancel booking, calculate totals.

### Nominal Flow
Booking request → API → BL validates → Repository checks availability  
→ Save booking → Create payment → API responds

### Alternatives
- 📆 Unavailable → error returned

### Loop
- Multiple bookings per user
- Multiple bookings per place

---

## ⭐ Review Management

**Role:** Post, update, or report reviews.

### Nominal Flow
API receives review → BL checks booking → Repository saves  
→ BL updates average rating → API responds

### Alternatives
- 🎫 Invalid booking → error returned

---

## 💳 Payment Management

**Role:** Process payments and refunds.

### Nominal Flow
API receives payment → BL validates → Repository saves  
→ BL returns confirmation → API responds

### Alternatives
- 💰 Refund success
- 💰 Refund failure

---

## 🧰 Amenity Management

**Role:** Create amenities and link to places.

### Nominal Flow
API receives amenity → BL validates → Repository saves → API responds

### Relationship
- Many-to-many between **Place ↔ Amenity**
- Implemented using a junction table

---

## 🛡️ Admin Management

**Role:** Manage admins, ban users, assign roles.

### Nominal Flow
Admin request → API → BL checks permissions  
→ Repository updates DB → API responds

### Alternatives
- 🔒 Unauthorized → error returned

---

## 💬 Message Management

**Role:** Send/receive messages, track read status.

### Nominal Flow — Sending
User sends message → API → BL validates → Repository saves  
→ BL returns → API responds

### Nominal Flow — Retrieving Conversation
Repository fetch → BL formats → API returns

---

# 🧑‍🏫 Tips

### 🧱 Separation of Responsibilities
Keep layers strictly separated:

# Layered Backend Architecture Notes

Client → API → Business Logic → Repository → Database

Each layer has a single responsibility.

---

## ✅ Validate First

Never trust user input blindly.  
Always validate data before touching the database.

---

## 🔀 Think in Alternatives & Loops

Every request has multiple possible outcomes:

- Success path
- Validation error
- Permission error
- Resource not found
- Loop scenarios (repeated actions)

Design for all of them.

---

## 🔗 Many-to-Many Relationships

Use junction tables:

PlaceAmenity  
place_id  
amenity_id  

This prevents duplication and keeps the database consistent.

---

## 🧭 Visualize the Flow

Every backend request follows:

Request → API → Business Logic → Repository → Database → Response

If a bug happens, check the chain step by step.

---

## 🗑️ Soft Deletes

Instead of deleting records permanently:

deleted_at = timestamp

This preserves history for audits, recovery, and debugging.

---

## ✅ Summary

A clean architecture is predictable:

- Each request follows a known path
- Errors are expected and handled
- Loops are controlled
- Relationships are explicit
- Data history is preserved

This structure scales well and is used in professional backend systems.
