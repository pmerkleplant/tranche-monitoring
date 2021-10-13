import json
import requests
from dataclasses import dataclass
from typing import Optional, List, Union
from decimal import Decimal

from web3 import Web3
from web3.types import ChecksumAddress, HexBytes

# ----------------------------------------------------------------------------------
# ------ Constants -----------------------------------------------------------------
# ----------------------------------------------------------------------------------

query_object_factory = '''\
    id,
    bondCount'''

query_object_token = '''\
    id,
    symbol,
    name,
    decimals,
    totalSupply'''

query_object_bond = '''\
    id,
    owners,
    collateral {
        id
    },
    tranches {
        id
    },
    maturityDate,
    isMature,
    totalDebt,
    totalCollateral'''

query_object_tranche = '''\
    id,
    bond {
        id
    },
    token {
        id
    },
    ratio,
    index,
    totalCollateral'''

query_object_account = '''\
    id,
    balances {
        id
    }'''

query_object_account_balance = '''\
    id,
    account {
        id
    },
    tranche {
        id
    },
    amount,
    block,
    modified,
    transaction'''


# ----------------------------------------------------------------------------------
# ------ Data classes --------------------------------------------------------------
# ----------------------------------------------------------------------------------

@dataclass
class Factory:
    id: ChecksumAddress
    bond_count: Decimal

    def __repr__(self) -> str:
        return f"Factory(id={self.id}, bondCount={self.bond_count})"

@dataclass
class Token:
    id: ChecksumAddress
    symbol: str
    name: str
    decimals: Decimal
    total_supply: Decimal

    def __repr__(self) -> str:
        return f"Token({self.name}, decimals={self.decimals}, totalSupply={self.total_supply})"

@dataclass
class Bond:
    id: ChecksumAddress
    owners: List[ChecksumAddress]
    collateral: ChecksumAddress
    tranches: List[ChecksumAddress]
    maturity_date: Decimal
    is_mature: bool
    total_debt: Decimal
    total_collateral: Decimal

    def _repr__(self) -> str:
        return f"Bond({self.id}, collateral={self.collateral}, totalDebt={self.total_debt}"

@dataclass
class Tranche:
    id: ChecksumAddress
    bond: ChecksumAddress
    token: ChecksumAddress
    ratio: Decimal
    index: Decimal
    total_collateral: Decimal

    def __repr__(self) -> str:
        return f"Tranche(id={self.id}, token={self.token}, bond={self.bond})"

@dataclass
class Balance:
    amount: Decimal
    tranche: ChecksumAddress

    def __repr__(self) -> str:
        return f"Balance(amount={self.amount}, tranche={self.tranche})"

@dataclass
class Account:
    id: ChecksumAddress
    account_balances: List[str]

    def __repr__(self) -> str:
        return f"Account(id={self.id}, firstBalance=({None if not self.account_balances else self.account_balances[0]}))"

@dataclass
class AccountBalances:
    id: str
    account: ChecksumAddress
    tranche: ChecksumAddress
    amount: Decimal
    block: Decimal
    modified: Decimal
    transaction: HexBytes

    def __repr__(self) -> str:
        return f"AccountBalances(account={self.account}, tranche={self.tranche}, amount={self.amount})"


# ----------------------------------------------------------------------------------
# ------ Parsers -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

def parse_factory(
    input: Union[dict, List]
) -> Optional[List[Factory]]:
    """
    Parses the given input dict to a list of Factory dataclass's.

    :param input:      Dict to parse
    :return:           List of Factory's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try:
        return [
            Factory(
                Web3.toChecksumAddress(elem['id']),
                Decimal(elem['bondCount'])
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to Factory failed')


def parse_token(
    input: Union[dict, List]
) -> Optional[List[Token]]:
    """
    Parses the given input dict to a list of Token dataclass's.

    :param input:      Dict to parse
    :return:           List of Token's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try:
        return [
            Token(
                Web3.toChecksumAddress(elem['id']),
                elem['symbol'],
                elem['name'],
                Decimal(elem['decimals']),
                Decimal(elem['totalSupply'])
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to Token failed')
    

def parse_bond(
    input: Union[dict, List]
) -> Optional[List[Bond]]:
    """
    Parses the given input dict to a list of Bond dataclass's.

    :param input:      Dict to parse
    :return:           List of Bond's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try:
        return [
            Bond(
                Web3.toChecksumAddress(elem['id']),
                [Web3.toChecksumAddress(owner) for owner in elem['owners']],
                Web3.toChecksumAddress(elem['collateral']['id']),
                [Web3.toChecksumAddress(tranche['id']) for tranche in elem['tranches']],
                Decimal(elem['maturityDate']),
                elem['isMature'],
                Decimal(elem['totalDebt']),
                Decimal(elem['totalCollateral'])
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to Bond failed')


def parse_tranche(
    input: Union[dict, List]
) -> Optional[List[Tranche]]:
    """
    Parses the given input dict to a list of Tranche dataclass's.

    :param input:      Dict to parse
    :return:           List of Tranche's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try:
        return [
            Tranche(
                Web3.toChecksumAddress(elem['id']),
                Web3.toChecksumAddress(elem['bond']['id']),
                Web3.toChecksumAddress(elem['token']['id']),
                Decimal(elem['ratio']),
                Decimal(elem['index']),
                Decimal(elem['totalCollateral'])
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to Tranche failed')


def parse_account(
    input: Union[dict, List]
) -> Optional[List[Account]]:
    """
    Parses the given input dict to a list of Account dataclass's.

    :param input:      Dict to parse
    :return:           List of Account's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try: 
        return [
            # NOTE: balance id = <accountAddress>-<tokenAddress>
            Account(
                Web3.toChecksumAddress(elem['id']),
                [balance['id'] for balance in elem['balances']]
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to Account failed')


def parse_account_balances(
    input: Union[dict, List]
) -> Optional[List[AccountBalances]]:
    """
    Parses the given input dict to a list of AccountBalance dataclass's.

    :param input:      Dict to parse
    :return:           List of AccountBalance's or None if input is empty
    :raise ValueError: If input is not parseable
    """
    input = to_list(input)
    if not input:
        return None

    try: 
        return [
            AccountBalances(
                elem['id'],
                Web3.toChecksumAddress(elem['account']['id']),
                Web3.toChecksumAddress(elem['tranche']['id']),
                Decimal(elem['amount']),
                Decimal(elem['block']),
                Decimal(elem['modified']),
                HexBytes(elem['transaction'])
            )
            for elem in input
        ]
    except Exception as e:
        raise ValueError('Parsing to AccountBalance failed')


# ----------------------------------------------------------------------------------
# ------ Query functions -----------------------------------------------------------
# ----------------------------------------------------------------------------------

def query_tokens(
    amount: int = -1,
    order_by: str = '',
    constraints: dict = {},
    direction_is_desc: bool = True
) -> Optional[List[Token]]:
    """
    Query all account balances ordered by `order_by` and filtered through `constraints`.
    Returns max `amount` Tokens.

    :param amount:            Max amount of Tokens to return
    :param order_by:          Field to order Tokens by
    :param constraints:       Dict with constraints for individual fields
    :param direction_is_desc: Order direction, default True
    :return:                  List of Tokens
    :raise ValueError:        If argument sanity check fails
    """
    try:
        sanity_check_arguments(query_object_token, order_by, constraints)
    except Exception as e:
        raise ValueError('sanity check arguments failed: ' + repr(e))

    order_args = build_ordered_arguments(amount, order_by, direction_is_desc)
    filter_args = build_filtered_arguments(constraints)

    args: str = ''
    if order_args and filter_args:
        args = (order_args + ', ' + filter_args)
    elif order_args:
        args = order_args
    elif filter_args:
        args = filter_args
    else:
        args = ''

    query = '''query {
        tokens('''+args+''') {
            '''+query_object_token+'''
        }
    }'''
    resp = send_subgraph_query(query)
    return parse_token(resp['data']['tokens'])


def query_accounts(
    amount: int = -1,
    order_by: str = '',
    constraints: dict = {},
    direction_is_desc: bool = True
) -> Optional[List[AccountBalances]]:
    """
    Query all accounts ordered by `order_by` and filtered through `constraints`.
    Returns max `amount` Accounts.

    :param amount:            Max amount of Accounts to return
    :param order_by:          Field to order Accounts by
    :param constraints:       Dict with constraints for individual fields
    :param direction_is_desc: Order direction, default True
    :return:                  List of Accounts
    :raise ValueError:        If argument sanity check fails
    """
    try:
        sanity_check_arguments(query_object_account, order_by, constraints)
    except Exception as e:
        raise ValueError('sanity check arguments failed: ' + repr(e))

    order_args = build_ordered_arguments(amount, order_by, direction_is_desc)
    filter_args = build_filtered_arguments(constraints)

    args: str = ''
    if order_args and filter_args:
        args = (order_args + ', ' + filter_args)
    elif order_args:
        args = order_args
    elif filter_args:
        args = filter_args
    else:
        args = ''

    query = '''query {
        accounts('''+args+''') {
            '''+query_object_account+'''
        }
    }'''
    resp = send_subgraph_query(query)
    return parse_account(resp['data']['accounts'])



def query_account_balances(
    amount: int = -1,
    order_by: str = '',
    constraints: dict = {},
    direction_is_desc: bool = True
) -> Optional[List[AccountBalances]]:
    """
    Query all account balances ordered by `order_by` and filtered through `constraints`.
    Returns max `amount` AccountBalances.

    :param amount:            Max amount of AccountBalances to return
    :param order_by:          Field to order AccountBalances by
    :param constraints:       Dict with constraints for individual fields
    :param direction_is_desc: Order direction, default True
    :return:                  List of AccountBalances
    :raise ValueError:        If argument sanity check fails
    """
    try:
        sanity_check_arguments(query_object_account_balance, order_by, constraints)
    except Exception as e:
        raise ValueError('sanity check arguments failed: ' + repr(e))

    order_args = build_ordered_arguments(amount, order_by, direction_is_desc)
    filter_args = build_filtered_arguments(constraints)

    args: str = ''
    if order_args and filter_args:
        args = (order_args + ', ' + filter_args)
    elif order_args:
        args = order_args
    elif filter_args:
        args = filter_args
    else:
        args = ''

    query = '''query {
        accountBalances('''+args+''') {
            '''+query_object_account_balance+'''
        }
    }'''
    resp = send_subgraph_query(query)
    return parse_account_balances(resp['data']['accountBalances'])


def query_tranches(
    amount: int = -1,
    order_by: str = '',
    constraints: dict = {},
    direction_is_desc: bool = True
) -> Optional[List[Tranche]]:
    """
    Query all tranches ordered by `order_by` and filtered through `constraints`.
    Returns max `amount` Tranches.

    :param amount:            Max amount of Tranches to return
    :param order_by:          Field to order Tranches by
    :param constraints:       Dict with constraints for individual fields
    :param direction_is_desc: Order direction, default True
    :return:                  List of Tranches
    :raise ValueError:        If argument sanity check fails
    """
    try:
        sanity_check_arguments(query_object_tranche, order_by, constraints)
    except Exception as e:
        raise ValueError('sanity check arguments failed: ' + repr(e))

    order_args = build_ordered_arguments(amount, order_by, direction_is_desc)
    filter_args = build_filtered_arguments(constraints)

    args: str = ''
    if order_args and filter_args:
        args = (order_args + ', ' + filter_args)
    elif order_args:
        args = order_args
    elif filter_args:
        args = filter_args
    else:
        args = ''

    query = '''query {
        tranches('''+args+''') {
            '''+query_object_tranche+'''
        }
    }'''
    resp = send_subgraph_query(query)
    return parse_tranche(resp['data']['tranches'])


def query_bonds(
    amount: int = -1,
    order_by: str = '',
    constraints: dict = {},
    direction_is_desc: bool = True
) -> Optional[List[Bond]]:
    """
    Query all bonds ordered by `order_by` and filtered through `constraints`.
    Returns max `amount` Bonds.

    :param amount:            Max amount of Bonds to return
    :param order_by:          Field to order Bonds by
    :param constraints:       Dict with constraints for individual fields
    :param direction_is_desc: Order direction, default True
    :return:                  List of Bonds
    :raise ValueError:        If argument sanity check fails
    """
    try:
        sanity_check_arguments(query_object_bond, order_by, constraints)
    except Exception as e:
        raise ValueError('sanity check arguments failed: ' + repr(e))

    order_args = build_ordered_arguments(amount, order_by, direction_is_desc)
    filter_args = build_filtered_arguments(constraints)

    args: str = ''
    if order_args and filter_args:
        args = (order_args + ', ' + filter_args)
    elif order_args:
        args = order_args
    elif filter_args:
        args = filter_args
    else:
        args = ''

    query = '''query {
        bonds('''+args+''') {
            '''+query_object_bond+'''
        }
    }'''
    resp = send_subgraph_query(query)
    return parse_bond(resp['data']['bonds'])


# ------ Query by ID ---------------------------------------------------------------

def query_factory_by_id(
    id: ChecksumAddress
) -> Optional[List[Factory]]:
    """
    Query factory information for specific factory id.

    :param id: Factory id
    :return:   List of Factory dataclass or None
    """
    query = '''query {
        factory(id: "'''+id.lower()+'''") {
            '''+query_object_factory+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_factory(resp['data']['factory'])


def query_token_by_id(
    id: ChecksumAddress
) -> Optional[List[Token]]:
    """
    Query token information for specific token id.

    :param id: Token id
    :return:   List of Token dataclass or None
    """
    query = '''query{
        token(id: "'''+id.lower()+'''") {
            '''+query_object_token+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_token(resp['data']['token'])


def query_bond_by_id(
    id: ChecksumAddress
) -> Optional[List[Bond]]:
    """
    Query bond information for specific bond id.

    :param id: Bond id
    :return:   List of Bond dataclass or None
    """
    query = '''query {
        bond(id: "'''+id.lower()+'''") {
            '''+query_object_bond+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_bond(resp['data']['bond'])


def query_tranche_by_id(
    id: ChecksumAddress
) -> Optional[List[Tranche]]:
    """
    Query tranche information for specific tranche id.

    :param id: Tranche id
    :return:   List of Tranche dataclass or None
    """
    query = '''query{
        tranche(id: "'''+id.lower()+'''") {
            '''+query_object_tranche+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_tranche(resp['data']['tranche'])


def query_account_by_id(
    id: ChecksumAddress
) -> Optional[List[Account]]:
    """
    Query account information for specific account id.

    :param id: Account id
    :return:   List of Account dataclass or None
    """
    query = '''query {
        account(id: "'''+id.lower()+'''") {
            '''+query_object_account+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_account(resp['data']['account'])


def query_account_balance_by_id(
    id: str
) -> Optional[List[AccountBalances]]:
    """
    Query account balance information for specific id.

    :param id: <AccountId>-<TokenId>
    :return:   List of AccountBalances dataclass or None
    """
    query = '''query {
        accountBalance(id: "'''+id.lower()+'''") {
            '''+query_object_account_balance+'''
        }
    }'''

    resp = send_subgraph_query(query)
    return parse_account_balances(resp['data']['accountBalance'])


# ----------------------------------------------------------------------------------
# ------ Helpers -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

def send_subgraph_query(query: str) -> dict:
    """
    Send given query to Buttonwoods's Tranche subgraph.

    :param query: The GraphQL query
    :return:      JSON parsed response's payload
    """
    subgraph_host = 'https://api.thegraph.com/subgraphs/name/marktoda/tranche'

    resp = requests.post(subgraph_host, json={'query': query})
    return json.loads(resp.text)


def to_list(input: Optional[Union[dict, List]]) -> Optional[List]:
    """
    Returns the input as list or None if empty.
    """
    if input:
        return input if isinstance(input, list) else [input]
    else:
        return None


def build_ordered_arguments(
    first: int, 
    order_by: str, 
    is_desc: bool
) -> str:
    """
    Returns a string to use in a GraphQL query for ordering.
    """
    direction = 'desc' if is_desc else 'asc'

    if first < 0:
        return '''orderBy: '''+order_by+''',
                  orderDirection: ''' + direction
    else:
        return '''first: '''+str(first)+''', 
                  orderBy: '''+order_by+''', 
                  orderDirection: '''+direction


def build_filtered_arguments(
    constraints: dict
) -> str:
    """
    Returns a string to use in a GraphQL query for filtering.
    """
    if not constraints:
        return ''

    filters = [
        str(field) + ": " + (f"\"{value}\"" if isinstance(value, str) else str(value))
        for field, value in constraints.items()
    ]

    result = 'where: { ' 
    ctr = 0
    for fil in filters:
        ctr += 1
        if ctr < len(filters):
            result += (fil + ', ')
        else:
            result += (fil + ' ')

    return result + '}'


def sanity_check_arguments(
    query_object: str,
    order_by: str,
    constraints: dict
) -> None:
    """
    Checks if order_by argument and each field in constraints exists
    as field in the query_object.

    Raises ValueError if not.
    """
    # Check that `order_by` field exists
    if not order_by in query_object:
        raise ValueError(f'{order_by} not a field')

    # Check that each `constraints` key exists
    for key in constraints.keys():
        field = key.split('_')[0]
        if not field in query_object:
            raise ValueError(f'{field} not a field')