Examples = [
    # Basic building information queries
    {
        "inputs": {
            "question": "What is the location of the BCGG shop?",
        },
        "outputs": {
            "response": "The BCGG shop is located in Roma Corso Francia"
        }
    },
    {
        "inputs": {
            "question": "How many buildings do we have in Milano?",
        },
        "outputs": {
            "response": "We have 2 buildings in Milano: Milano Via Padova (BCGN shop) and Milano City Life (BCGY shop)"
        }
    },
    {
        "inputs": {
            "question": "What's the area of the Bussolengo building?",
        },
        "outputs": {
            "response": "The Bussolengo building has an area of 1527 square meters, making it the largest building in our portfolio"
        }
    },
    
    # Temperature sensor queries
    {
        "inputs": {
            "question": "How many temperature sensors are in the BCGW ?",
        },
        "outputs": {
            "response": "The BCGW shop in Bussolengo has 7 zone air temperature sensors and 1 outside air temperature sensor, for a total of 8 temperature sensors"
        }
    },
    {
        "inputs": {
            "question": "Give me the UUID for the outside temperature sensor at the Roma Corso Francia building",
        },
        "outputs": {
            "response": "The outside air temperature sensor at Roma Corso Francia has UUID: dd0dc527-28f9-486a-b5c4-b009b6f2a64f"
        }
    },
    
    # Zone-specific queries
    {
        "inputs": {
            "question": "Which zones exist in Grottaminarda?",
        },
        "outputs": {
            "response": "The BCGR shop in Grottaminarda has 4 zones: Zone_1, Zone_2, Zone_3, and Zone_4"
        }
    },
    {
        "inputs": {
            "question": "What's the temperature sensor UUID for Zone_3 in BCGX?",
        },
        "outputs": {
            "response": "The temperature sensor in Zone_3 of the BCGX shop (Cesenatico) has UUID: 90180e55-2803-4da7-9ff1-279f0f472873"
        }
    },
    
    # Meter and energy queries
    {
        "inputs": {
            "question": "What meters are available for the BCGU shop in Monopoli?",
        },
        "outputs": {
            "response": "The BCGU shop in Monopoli has 2 meters: Main Electric Meter (UUID: 18166543-a2f7-46b1-bab2-f5eeb610d731) and HVAC Electric Meter (UUID: ab81da91-504b-4ff0-908c-fa188b09cdd3)"
        }
    },
    
    # Coordinate and location queries
    {
        "inputs": {
            "question": "What are the coordinates of the Castelfranco building?",
        },
        "outputs": {
            "response": "The Castelfranco building is located at coordinates: latitude 45.68591, longitude 11.95689"
        }
    },
    
    # Multi-building comparison queries
    {
        "inputs": {
            "question": "Which building has the smallest area?",
        },
        "outputs": {
            "response": "The Building_Roma_Corso_Francia or also know as BCGG building has the smallest area at 171 square meters"
        }
    },
    {
        "inputs": {
            "question": "List all buildings with their areas sorted from largest to smallest",
        },
        "outputs": {
            "response": "Buildings sorted by area (largest to smallest):\n1. Bussolengo: 1527 sq m\n2. Alessandria: 589 sq m\n3. Nola: 541 sq m\n4. Roma Prenestina: 515 sq m\n5. Darfo Boario Terme: 439 sq m\n6. Cesenatico: 399 sq m\n7. Ascoli: 398 sq m\n8. Osimo: 397 sq m\n9. Medolago: 400 sq m\n10. Oderzo: 394 sq m\n11. Fidenza: 379 sq m\n12. Cattolica: 370 sq m\n13. Cremona: 367 sq m\n14. Grottaminarda: 340 sq m\n15. Castiglione delle Stiviere: 287 sq m\n16. Monopoli: 285 sq m\n17. Milano City Life: 209 sq m\n18. Milano Via Padova: 178 sq m\n19. Roma Corso Francia: 171 sq m"
        }
    },
    
    # Error handling / edge cases
    {
        "inputs": {
            "question": "What sensors are in the BCG999 shop?",
        },
        "outputs": {
            "response": "I couldn't find any shop with the code BCG999 in our building database. Please check the shop code and try again."
        }
    },
    {
        "inputs": {
            "question": "How many buildings do we have in Paris?",
        },
        "outputs": {
            "response": "We don't have any buildings located in Paris. All our buildings are located in Italy."
        }
    },
    
    # Complex multi-step queries
    {
        "inputs": {
            "question": "I need to do maintenance on all temperature sensors in buildings larger than 400 square meters. Which sensors should I check?",
        },
        "outputs": {
            "response": "For buildings larger than 400 sq m, you need to check temperature sensors in:\n- Bussolengo (1527 sq m): 8 sensors\n- Alessandria (589 sq m): 5 sensors  \n- Nola (541 sq m): 5 sensors\n- Roma Prenestina (515 sq m): 5 sensors\n- Darfo Boario Terme (439 sq m): 5 sensors\nI can provide specific UUIDs for each sensor if needed."
        }
    },
    
    # Brick schema specific queries
    {
        "inputs": {
            "question": "What types of sensors do we have across all buildings?",
        },
        "outputs": {
            "response": "We have two main types of temperature sensors: Zone_Air_Temperature_Sensors (for monitoring indoor zones) and Outside_Air_Temperature_Sensors (for monitoring external conditions). We also have various types of meters including Electric_Power_Sensors, Electric_Energy_Sensors, and general Meters."
        }
    },
    
    # Maintenance/operational queries
    {
        "inputs": {
            "question": "Which building has the most zones and how many sensors does it have?",
        },
        "outputs": {
            "response": "The BCGW shop in Bussolengo has the most zones (7 zones: Zone_1, Zone_2, Zone_3, Zone_4, Zone_8, Zone_9, Zone_10) with 7 zone temperature sensors plus 1 outside temperature sensor, totaling 8 sensors."
        }
    },
    
    # Geographic clustering
    {
        "inputs": {
            "question": "Group our buildings by geographic region in Italy",
        },
        "outputs": {
            "response": "Buildings grouped by Italian regions:\n\nNorthern Italy:\n- Milano (2 buildings): Via Padova, City Life\n- Bussolengo, Castelfranco, Medolago, Oderzo, Darfo Boario Terme, Castiglione delle Stiviere, Fidenza, Cremona, Alessandria\n\nCentral Italy:\n- Roma (2 buildings): Corso Francia, Prenestina\n- Cesenatico, Ascoli, Cattolica, Osimo\n\nSouthern Italy:\n- Nola, Grottaminarda, Monopoli"
        }
    }
]