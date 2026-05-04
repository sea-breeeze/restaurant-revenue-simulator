#Main Core
import random, json

def roll(chance):
    return random.random() < ( chance / 100)


def probabilityOfItems(menu_set):
    """Generates random probability you'd have of picking certain item based on percentage"""
    results = {}
    extra_chances = 50

    for items, data in menu_set.items():
        count = 0

        if roll(data['Percentage']):
            count += 1

            while roll(extra_chances):
                count += 1
        
        results[items] = count


    return results


def allCustomersProbability(customerCount, menu):
    """Generates the probabiliy of each customer picking an item"""
    customerResults = {}
    
    for i in range(customerCount):
        customerResults[f"Customer {i+1}"] = probabilityOfItems(menu)

    return customerResults

def totalCustomerItemsSold(customersOrders):
    """ total units sold per item across all customers for a single day """
    total = {}

    for items in customersOrders.values():
        for item, count in items.items():
            total[item] = total.get(item, 0) + count

    return total

def totalCustomersItemsRevenue(totalSold, menu):
    """Calculates total revenue per item given units sold and menu prices."""
    revenue = {}

    for item, count in totalSold.items():
        price = menu[item]['Price']
        revenue[item] = revenue.get(item, 0) + (count * price)

    return revenue


def run_single_simulation(days, menu, base_customers):
    """Randomizes daily items and revenue sold throughout user inputted dates and range"""

    daily_revenue = {}
    daily_items = {}

    for day in range(days):
        customerCount = int(base_customers * random.uniform(0.8, 1.2))
        customersOrders = allCustomersProbability(customerCount, menu)
        totalSold = totalCustomerItemsSold(customersOrders)
        revenue = totalCustomersItemsRevenue(totalSold, menu)

        day_key = f"Day {day+1}"

        daily_items[day_key] = totalSold.copy()
        daily_revenue[day_key] = revenue.copy()


    return daily_revenue, daily_items

def save_config(menu, days, customers, simulations, filename="config.json"):
    config = {
        "menu": menu,
        "days": days,
        "customers": customers,
        "simulations": simulations
    }
    with open(filename, "w") as f:
        json.dump(config, f, indent=4)

def load_config(filename="config.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def monte_carlo_simulation(days, menu, base_customers, simulations=10):
    """Runs multiple simulations to be able to view data on set amount of simulations"""
    results = []

    for __ in range(simulations):
        daily_revenue, _ = run_single_simulation(days, menu, base_customers)

        total_revenue = sum(
            sum(day.values()) for day in daily_revenue.values()
        )

        results.append(total_revenue)

    return results

