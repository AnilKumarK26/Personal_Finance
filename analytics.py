from datetime import datetime, timedelta
from database import transactions_collection

def get_summary():
    """Get monthly summary"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    pipeline = [
        {'$match': {'date': {'$gte': start_of_month}}},
        {'$group': {'_id': '$type', 'total': {'$sum': '$amount'}, 'count': {'$sum': 1}}}
    ]
    
    results = list(transactions_collection.aggregate(pipeline))
    summary = {'total_income': 0, 'total_expenses': 0, 'net_balance': 0, 'income_count': 0, 'expense_count': 0}
    
    for result in results:
        if result['_id'] == 'income':
            summary['total_income'] = result['total']
            summary['income_count'] = result['count']
        elif result['_id'] == 'expense':
            summary['total_expenses'] = result['total']
            summary['expense_count'] = result['count']
    
    summary['net_balance'] = summary['total_income'] - summary['total_expenses']
    return summary

def get_expenses_by_category(start_date=None, end_date=None):
    """Get expenses grouped by category"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    date_query = {}
    if start_date:
        date_query['$gte'] = datetime.fromisoformat(start_date)
    else:
        now = datetime.now()
        date_query['$gte'] = datetime(now.year, now.month, 1)
    
    if end_date:
        date_query['$lte'] = datetime.fromisoformat(end_date)
    
    pipeline = [
        {'$match': {'type': 'expense', 'date': date_query}},
        {'$group': {'_id': '$category', 'total_amount': {'$sum': '$amount'}, 'count': {'$sum': 1}}},
        {'$sort': {'total_amount': -1}}
    ]
    
    results = list(transactions_collection.aggregate(pipeline))
    categories = [r['_id'] for r in results]
    amounts = [r['total_amount'] for r in results]
    
    return {
        'categories': categories,
        'amounts': amounts,
        'total_categories': len(categories),
        'total_amount': sum(amounts)
    }

def get_monthly_trend():
    """Get 6-month trend data"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    pipeline = [
        {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
        {'$group': {
            '_id': {'year': {'$year': '$date'}, 'month': {'$month': '$date'}, 'type': '$type'},
            'total': {'$sum': '$amount'}
        }},
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]
    
    results = list(transactions_collection.aggregate(pipeline))
    monthly_data = {}
    
    for result in results:
        month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        monthly_data[month_key][result['_id']['type']] = result['total']
    
    return monthly_data
