from typing import (
    Optional,
    List
)

from flask import (
    Flask,
    render_template,
    url_for
)
from web3 import Web3
from web3.types import ChecksumAddress

import subgraph


app = Flask(__name__)


@app.route('/')
def get_index():
    html: str = render_template('header.html') + '<body>'

    # Demo links
    html += '<u>Demo links</u>:<p>'
    bonds_url = url_for('serve_bonds_info')
    html += f'Check out all <a href={bonds_url}>bonds</a><p>'
    bond_url = url_for('serve_specific_bond_info', id='0x8B3ea6492d25796346Aa8a2C2e63Da3E9e0EF75A')
    html += f'Check out a specific bond, i.e. <a href={bond_url}>0x8B3ea6492d25796346Aa8a2C2e63Da3E9e0EF75A</a><p>'
    account_url = url_for('serve_specific_account_info', id='0xd6F3804860f1cCa51dAE87A714dDB1A1EC60a619')
    html += f'Check out a specific account, i.e. <a href={account_url}>0xd6F3804860f1cCa51dAE87A714dDB1A1EC60a619</a><p>'
    tranche_url = url_for('serve_specific_tranche_info', id='0xAAA35282144C902d908a8a93dBc1e2bF36A6f5C7')
    html += f'Check out a specific tranche, i.e. <a href={tranche_url}>0xAAA35282144C902d908a8a93dBc1e2bF36A6f5C7</a><p>'

    ctr = 0
    ### Get accounts with most balances
    accounts: Optional[List[subgraph.Account]] = subgraph.query_accounts(order_by='id')
    if not accounts:
        return f'ERROR: No accounts found'

    accounts_sorted = sorted(
        accounts,
        key=lambda account: len(account.account_balances)
    )

    legend = 'Accounts with most different balances'
    labels = [
        account.id
        for account in accounts_sorted
    ]
    values = [
        len(account.account_balances)
        for account in accounts_sorted
    ]
    html += render_template('bar_chart.html', 
                            title='Accounts with most different balances',
                            ctr=ctr, legend=legend, labels=labels, values=values)


    ctr += 1
    ### Tokens
    tokens: Optional[List[subgraph.Token]] = subgraph.query_tokens(amount=10, order_by='totalSupply')
    if not tokens:
        return f'No Tokens found'


    legend = 'Tokens with highest total supply'
    labels = [
        token.symbol
        for token in tokens
    ]
    values = [
        token.total_supply/10**token.decimals
        for token in tokens
    ]

    html += render_template('bar_chart.html', 
                            title='Tokens with highest total supply',
                            ctr=ctr, legend=legend, labels=labels, values=values)

    return html + '</body>'

# TODO: Make a list with links right next to chart with the addresses

@app.route('/account/<id>')
def serve_specific_account_info(id: str):
    html: str = render_template('header.html') + '<body>'

    try:
        id = Web3.toChecksumAddress(id)
    except ValueError as e:
        return f'ERROR: Given id could not be formatted to Ethereum Address'

    # Get account by id
    accounts = subgraph.query_account_by_id(id)
    if not accounts:
        return f'Account({id}) not found!'
    account = accounts.pop()

    # Render basic account information
    # TODO: Template basic account information
    html += f'Account: {account.id}<p>'

    # Serve information about each AccountBalance
    ctr = 0
    for account_balance_id in account.account_balances:
        # Query AccountBalance
        account_balances = subgraph.query_account_balance_by_id(account_balance_id)
        if not account_balances:
            html += f'<p>No accountBalance found for id: {account_balance_id}<p>'
            continue
        ab = account_balances.pop()

        # Get the tranche's token to calculate the amount
        tranches = subgraph.query_tranche_by_id(ab.tranche)
        if not tranches:
            html += f'<p>Tranche {ab.tranche} not found for accountBalance {account_balance_id}'
            continue
        tranche = tranches.pop()
        tokens = subgraph.query_token_by_id(tranche.token)
        if not tokens:
            html += f'<p>Token {tranche.token} not found for accountBalance {account_balance_id}'
            continue
        token = tokens.pop()

        html += f'<u>AccountBalance {ctr}:</u><p>'
        tranche_url = url_for('serve_specific_tranche_info', id=ab.tranche)
        html += f'Tranche: <a href={tranche_url}>{ab.tranche}</a><p>'
        html += f'Token: {token.symbol}<p>'
        html += f'Amount: {ab.amount/10**token.decimals}<p>'

        ctr += 1

    return html + '</body>'


@app.route('/bond/<id>')
def serve_specific_bond_info(id: str):
    html: str = render_template('header.html') + '<body>'

    try:
        id = Web3.toChecksumAddress(id)
    except ValueError as e:
        return f'ERROR: Given id could not be formatted to Ethereum Address'

    # Get bond by id
    bonds = subgraph.query_bond_by_id(id)
    if not bonds:
        return f'Bond({id}) not found!'
    bond = bonds.pop()

    # Get bond's collateral token
    collaterals = subgraph.query_token_by_id(bond.collateral)
    if not collaterals:
        return f'Token({bond.collateral}) not found!'
    collateral = collaterals.pop()

    # Render basic bond information
    html += f'Bond info: ID: {bond.id}, Collateral: {collateral.symbol}, isMature: {bond.is_mature}'
    # TODO: Template basic bond info

    # Serve information about each tranche
    ctr = 0
    for tranche in bond.tranches:
        # Get owner's of this tranche, ordered by amount
        owners = subgraph.query_account_balances(order_by='amount', constraints={
            'tranche': tranche.lower()
        })
        if not owners:
            html += f'<p>No owners found to tranche: {tranche}<p>'
            continue

        legend = f'Holders of Tranche: {tranche}'
        labels = [ owner.account for owner in owners ]
        values = [ owner.amount/10**collateral.decimals for owner in owners ]

        tranche_url = url_for('serve_specific_tranche_info', id=tranche)
        html += f'<p>Tranche: <a href={tranche_url}>{tranche}</a>'

        html += render_template('pie_chart.html', 
                                title=f'Holders:',
                                ctr=ctr, legend=legend, labels=labels, values=values)

        # Add link for each account to account's page
        links = [
            '<a href=' + url_for('serve_specific_account_info', id=owner.account) + '>' + owner.account + '</a>'
            for owner in owners
        ]
        for link in links:
            html += '<p>' + link

        ctr += 1

    return html + '</body>'


@app.route('/bonds')
def serve_bonds_info():
    html: str = render_template('header.html') + '<body>'

    # Get all bonds, sorted by isMature=False
    bonds = subgraph.query_bonds(order_by='isMature', direction_is_desc=False)
    if not bonds:
        return f'ERROR: Could not query bonds'

    # Serve information about each bond
    for bond in bonds:
        # Get bond's collateral token
        collaterals = subgraph.query_token_by_id(bond.collateral)
        if not collaterals:
            return f'Token({bond.collateral}) not found!'
        collateral = collaterals.pop()

        # Add info to html
        html += '<p>'
        html += f'Bond info: ID: {bond.id}, Collateral: {collateral.symbol}, isMature: {bond.is_mature}'
        bond_url = url_for('serve_specific_bond_info', id=bond.id)
        html += f'<p><a href={bond_url}>link</a>'
        # TODO: Template basic bond info

    return html + '</body>'


@app.route('/tranche/<id>')
def serve_specific_tranche_info(id: str):
    html: str = render_template('header.html') + '<body>'

    try:
        id_checked = Web3.toChecksumAddress(id)
    except ValueError as e:
        return f'ERROR: Given id could not be formatted to Ethereum Address'

    tranches = subgraph.query_tranche_by_id(id_checked)
    if not tranches:
        return f'Tranche({id}) not found!'
    tranche = tranches.pop()

    # Get tranche's token info
    tokens = subgraph.query_token_by_id(tranche.token)
    if not tokens:
        return f'No Token found with id {tranche.token}'
    token = tokens.pop()

    # Render basic tranche information
    html += f'Tranche info: id={tranche.id}, token={token.symbol}, totalCollateral={tranche.total_collateral}<p>'
    bond_url = url_for('serve_specific_bond_info', id=tranche.bond)
    html += f'Bond: <a href={bond_url}>{tranche.bond}</a>'

    # Get owner's of this tranche, ordered by amount
    owners = subgraph.query_account_balances(order_by='amount', constraints={
        'tranche': tranche.id.lower()
    })
    if not owners:
        html += f'<p>No owners found to tranche: {tranche.id}<p>'
        return html

    legend = f'Holders of Tranche: {tranche.id}'
    labels = [ owner.account for owner in owners ]
    values = [ owner.amount/10**token.decimals for owner in owners ]

    html += render_template('pie_chart.html', 
                            title=f'Holders of Tranche: {tranche.id}',
                            ctr=0, legend=legend, labels=labels, values=values)

    # Add link for each account to account's page
    links = [
        '<a href=' + url_for('serve_specific_account_info', id=owner.account) + '>' + owner.account + '</a>'
        for owner in owners
    ]
    for link in links:
        html += '<p>' + link

    return html + '</body>'