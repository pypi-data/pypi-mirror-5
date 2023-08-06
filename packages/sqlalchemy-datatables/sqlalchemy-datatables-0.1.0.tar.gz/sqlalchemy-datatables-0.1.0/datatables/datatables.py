# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql import or_

from collections import namedtuple

ColumnTuple = namedtuple('ColumnDT', ['column_name', 'mData', 'filter'])

class ColumnDT(ColumnTuple):
    """Class defining a DataTables Column with a ColumnTuple:

    :param column_name: name of the column as defined by the SQLAlchemy model
    :type column_name: str
    :param mData: name of the mData property as defined in the DataTables javascript options (default None)
    :type mData: str
    :param filter: the method needed to be executed on the cell values of the column 
    as an equivalent of a jinja2 filter (default None)
    :type filter: a callable object

    :returns: a ColumnDT object 
    """
    def __new__(cls, column_name, mData=None, filter=None):
        """On creation, sets default None values for mData and filter
        """
        return super(ColumnDT, cls).__new__(cls, column_name, mData, filter)


class DataTables:
    """Class defining a DataTables object with:

    :param request: request containing the GET values, specified by the 
    datatable for filtering, sorting and paging
    :type request: pyramid.request
    :param sqla_object: your SQLAlchemy table object
    :type sqla_object: sqlalchemy.ext.declarative.DeclarativeMeta
    :param query: the query wanted to be seen in the the table
    :type query: sqlalchemy.orm.query.Query
    :param columns: columns specification for the datatables
    :type columns: list

    :returns: a DataTables object
    """
    def __init__(self, request, sqla_object, query, columns):
        """Initializes the object with the attributes needed, and runs the query
        """
        self.request_values = request.GET
        self.sqla_object = sqla_object
        self.query = query
        self.columns = columns
        self.results = None

        # total in the table after filtering
        self.cardinality_filtered = 0

        # total in the table unfiltered
        self.cardinality = 0

        self.run()


    def output_result(self):
        """Outputs the results in the format needed by DataTables
        """
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        
        output['aaData'] = self.results
 
        return output


    def run(self):
        """Launch filtering, sorting and paging processes to output results
        """
        # count before filtering
        self.cardinality = self.query.count()
        
        # the term entered in the datatable's search box
        self.filtering()

        # field chosen to sort on
        self.sorting()

        # pages have a 'start' and 'length' attributes
        self.paging()

        # fetch the result of the queries
        self.results = self.query.all()

        #return formatted results with correct filters applied
        formatted_results = []
        for i in range(len(self.results)):
            row = dict()
            for j in range(len(self.columns)):
                col = self.columns[j]
                if col.filter:
                    row[col.mData if col.mData else str(j)] = col.filter(getattr(self.results[i], col.column_name))
                else:
                    row[col.mData if col.mData else str(j)] = getattr(self.results[i], col.column_name)
            formatted_results.append(row)

        self.results = formatted_results


    def filtering(self):
        """Construct the query, by adding filtering(LIKE) on all columns when the datatable's search box is used
        """
        search_value = self.request_values.get('sSearch')
        conditions = []

        if(search_value) and (search_value != ""):
            for col in self.columns:
                conditions.append(getattr(self.sqla_object, col.column_name).like("%" + search_value + "%"))

            condition = or_(*conditions)
            print condition
            self.query = self.query.filter(condition)
            
            # count after filtering
            self.cardinality_filtered = self.query.count()
        else:
            self.cardinality_filtered = self.cardinality


    def sorting(self):
        """Construct the query, by adding sorting(ORDER BY) on the columns needed to be applied on
        """
        sorting = []

        Order = namedtuple('order', ['name', 'dir'])

        if ( self.request_values.get('iSortCol_0') != "" ) \
            and ( self.request_values.get('iSortingCols') > 0 ):

            for i in range(int(self.request_values['iSortingCols'])):
                sorting.append(Order( self.columns[int(self.request_values['iSortCol_'+str(i)])].column_name,
                        self.request_values['sSortDir_'+str(i)]))

        for sort in sorting:
            self.query = self.query.order_by(
                asc(sort.name) if sort.dir == 'asc' else desc(sort.name))


    def paging(self):
        """Construct the query, by slicing the results in order to limit rows showed on the page, and paginate the rest
        """
        pages = namedtuple('pages', ['start', 'length'])

        if (self.request_values['iDisplayStart'] != "" ) \
            and (self.request_values['iDisplayLength'] != -1 ):
            pages.start = int(self.request_values['iDisplayStart'])
            pages.length = int(self.request_values['iDisplayLength'])

        offset = pages.start + pages.length
        self.query = self.query.slice(pages.start, offset)