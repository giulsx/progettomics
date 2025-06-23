# Product & Activity API - `routes/product_routes.py`

## 🔧 Endpoints

### 1. **Crea un nuovo prodotto**
- **POST** `/products`
- **Input JSON:**
```json
{
  "productname": "Scarpa eco",
  "systemmodel": "APOS",
  "intervallo": "2023",
  "totale_produzione": 10000,
  "userid": "user-uuid"
}
```
- **Output:**
```json
{
  "message": "Prodotto creato",
  "productid": "uuid-generato"
}
```

---

### 2. **Suggerimenti di prodotti esistenti (autocomplete)**
- **GET** `/products/suggestions?userid=<user-id>&query=<text>`
- **Output:**
```json
[
  {
    "productid": "uuid",
    "productname": "Scarpa eco",
    "systemmodel": "APOS",
    "intervallo": "2023",
    "totale_produzione": 10000
  }
]
```

---

### 3. **Recupera tutte le ISIC Section**
- **GET** `/isicsections`
- **Output:**
```json
[
  { "code": "C", "name": "Manufacturing" }
]
```

---

### 4. **Filtra attività per ISIC Section e System Model**
- **GET** `/activities/filter?systemmodel=APOS&isicsection=C`
- **Output:**
```json
[
  {
    "id": "uuid",
    "name": "Produzione suola"
  }
]
```

---

### 5. **Dettagli attività (geography inclusa)**
- **GET** `/activities/<activity_id>`
- **Output:**
```json
{
  "id": "uuid",
  "name": "Produzione suola",
  "location": "EU"
}
```

---

### 6. **Attività di trasporto**
- **GET** `/transport-activities`
- **Output:**
```json
[
  {
    "id": "uuid",
    "name": "Trasporto su gomma",
    "location": "IT"
  }
]
```

---

### 7. **Fornitore di un’attività**
- **GET** `/activities/<activity_id>/fornitore`
- **Output:**
```json
{
  "fornitore": "nome_fornitore"
}
```

---

### 8. **Unità di misura del prodotto di riferimento di un’attività**
- **GET** `/activities/<activity_id>/unita_misura`
- **Output:**
```json
{
  "unitname": "kg"
}
```

---

### 9. **Associa attività a un prodotto**
- **POST** `/product-activity`
- **Input JSON:**
```json
{
  "productid": "uuid-prodotto",
  "activityid": "uuid-attività",
  "amount": 100,
  "fase_generale": "Upstream",
  "fase_produttiva": "Materia Prima",
  "distanza_fornitore": 120,
  "id_mezzo_activity": "uuid-mezzo"
}
```
- **Output:**
```json
{
  "message": "Associazione creata con successo"
}
```

---

### 10. **Rimuovi attività da un prodotto**
- **DELETE** `/products/<productid>/activities/<activityid>?fase=<fase>`
- **Output:**
```json
{
  "message": "Attività rimossa dal prodotto"
}
```

---

### 11. **Visualizza attività associate a un prodotto per fase**
- **GET** `/products/<productid>/activities?fase=<fase>`
- **Output:**
```json
[
  {
    "id": "uuid-attività",
    "name": "Produzione suola",
    "amount": "100.0",
    "fase": "Upstream"
  }
]
```



 
