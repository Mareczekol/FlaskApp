from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)


@app.route('/')
def home():
    account = load_account()
    inventory = load_inventory()
    return render_template('home.html', account=account, inventory=inventory)


@app.route('/purchase', methods=['POST'])
def purchase():
    product_name = request.form['product_name']
    price = request.form['price']
    quantity = request.form['quantity']

    if not product_name or not price or not quantity:
        error_message = "Please fill in all the fields."
        inventory = load_inventory()
        return render_template('home.html', error_message=error_message, inventory=inventory)

    price = float(price)
    quantity = int(quantity)

    inventory = load_inventory()
    if product_name in inventory:
        inventory[product_name][1] += quantity
    else:
        inventory[product_name] = [price, quantity]

    account = load_account()
    account -= price * quantity

    action = ("purchase", product_name, price, quantity)
    save_action(action)

    save_account(account)
    save_inventory(inventory)

    return redirect(url_for('home'))


@app.route('/sale', methods=['POST'])
def sale():
    product_name = request.form['product_name']
    quantity = request.form['quantity']

    if not product_name or not quantity:
        error_message = "Please fill in all the fields."
        inventory = load_inventory()
        return render_template('home.html', error_message=error_message, inventory=inventory)

    quantity = int(quantity)

    inventory = load_inventory()
    if product_name in inventory and inventory[product_name][1] >= quantity:
        inventory[product_name][1] -= quantity
        price = inventory[product_name][0]
        account = load_account()
        account += price * quantity

        action = ("sale", product_name, price, quantity)
        save_action(action)

        save_account(account)
        save_inventory(inventory)

    return redirect(url_for('home'))


@app.route('/change_balance', methods=['POST'])
def change_balance():
    amount = request.form['amount']

    if not amount:
        error_message = "Please enter an amount."
        account = load_account()
        inventory = load_inventory()
        return render_template('home.html', error_message=error_message, account=account, inventory=inventory)

    try:
        amount = float(amount)
        if amount < 0:
            error_message = "Please enter a positive amount."
            account = load_account()
            inventory = load_inventory()
            return render_template('home.html', error_message=error_message, account=account, inventory=inventory)
    except ValueError:
        error_message = "Invalid amount. Please enter a valid number."
        account = load_account()
        inventory = load_inventory()
        return render_template('home.html', error_message=error_message, account=account, inventory=inventory)

    account = load_account()
    account += amount

    action = ("change_balance", amount)
    save_action(action)

    save_account(account)

    return redirect(url_for('home'))


@app.route('/historia', methods=['GET', 'POST'])
def history():
    actions = load_actions()
    start = request.args.get('start')
    end = request.args.get('end')

    if start and end:
        try:
            start = int(start)
            end = int(end)
            actions = actions[start:end]
        except (ValueError, IndexError):
            start = None
            end = None

    return render_template('history.html', actions=actions, start=start, end=end)


def load_account():
    if not os.path.exists('account.txt'):
        with open('account.txt', 'w') as account_file:
            account_file.write('0')
    else:
        with open('account.txt', 'r') as account_file:
            return float(account_file.read().strip())


def save_account(account):
    with open('account.txt', 'w') as account_file:
        account_file.write(str(account))


def load_inventory():
    inventory = {}
    if os.path.exists('inventory.txt'):
        with open('inventory.txt', 'r') as inventory_file:
            for line in inventory_file:
                product, price, quantity = line.strip().split(',')
                inventory[product] = [float(price), int(quantity)]
    return inventory


def save_inventory(inventory):
    with open('inventory.txt', 'w') as inventory_file:
        for product, details in inventory.items():
            inventory_file.write(f"{product},{details[0]},{details[1]}\n")


def load_actions():
    actions = []
    if os.path.exists('actions.txt'):
        with open('actions.txt', 'r') as actions_file:
            for line in actions_file:
                action = eval(line.strip())
                actions.append(action)
    return actions


def save_action(action):
    with open('actions.txt', 'a') as actions_file:
        actions_file.write(str(action) + '\n')


if __name__ == '__main__':
    app.run()
