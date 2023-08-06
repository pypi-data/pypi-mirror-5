# -*- encoding: utf-8 -*-
'''
Manage connection to and querying over an RDF dataset
for an Akara web application

Requires a configuration section, for example:

class dataset:
    mysqlDataset = {
        'type'         : "MySQL",
        'mysqldb'      : "[..]",
        'mysqluser'    : "[..]",
        'mysqlhost'    : "[..]",
        'mysqlpw'      : "[..]",
        'mysqlStoreId' : "[..]",
        'mysqlPort'    : "[..]"
    }

    #result XSLT directory
    result_xslt_directory = ".. /path/to/xslt/dir .."

    #Graph store to back GSP
    graph_store_name         = " .. dataset name .."
    graph_store_url          = " .. URL of GSP .."
    external_graph_store_url = ".. external URL of GSP (if different from above) .."

    #Triclops configuration
    datastore_owl = "/path/to/owl/file"
    debugQuery = True|False
    NO_BASE_RESOLUTION = True|False
    IgnoreQueryDataset = True|False
    endpointURL        = .. see: http://www.w3.org/TR/sparql11-service-description/#sd-endpoint ..

    sparqlQueryFiles = "/path/to/query/files"
    nsPrefixes       = { "..prefix.." : rdflib.Namespace  }

    sqlLiteralProps  = [ .., .., .. ]
    sqlResourceProps = [ .., .., .. ]
'''

import os, akara, time
from akara import registry
from rdflib import plugin, URIRef, OWL, RDFS, RDF, BNode
from rdflib.store import Store, NO_STORE
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib.store.SPARQL import GET,POST

OWL_PROPERTIES_QUERY=\
"""
SELECT ?literalProperty ?resourceProperty
WHERE {
    { ?literalProperty a owl:DatatypeProperty }
                    UNION
    { ?resourceProperty a ?propType
      FILTER(
        ?propType = owl:ObjectProperty ||
        ?propType = owl:TransitiveProperty ||
        ?propType = owl:SymmetricProperty ||
        ?propType = owl:InverseFunctionalProperty )  }
}"""

def GetGraphStoreForProtocol():
    configDict = akara.module_config()
    return configDict.get('graph_store_name'), configDict.get('graph_store_url')

def GetExternalGraphStoreURL():
    configDict = akara.module_config()
    return configDict.get('external_graph_store_url')

def ConfigureTriclops(datasetName,nsBindings,litProps,resProps):
    """
    Adapts akara configuration to Triclops configuration
    """
        #ontGraph,
        #ruleSet,
        #definingOntology,
        #builtinTemplateGraph,
        #defaultDerivedPreds):
    datasetConfig = akara.module_config().get(datasetName)
    connectStr = 'user=%s,password=%s,db=%s,port=%s,host=%s' % (
        datasetConfig.get('mysqluser'),
        datasetConfig.get('mysqlpw'),
        datasetConfig.get('mysqldb'),
        datasetConfig.get('mysqlPort',3306),
        datasetConfig.get('mysqlhost')
    )
    triclopsConf = {
        'result_xslt_directory' : akara.module_config().get('result_xslt_directory'),
        'store_identifier'      : datasetConfig.get('mysqlStoreId'),
        'connection'            : connectStr,
        'store'                 : datasetConfig.get('type'),
        'debugQuery'            : akara.module_config().get('debugQuery',False),
        'NO_BASE_RESOLUTION'    : akara.module_config().get('NO_BASE_RESOLUTION',False),
        'IgnoreQueryDataset'    : akara.module_config().get('IgnoreQueryDataset',False),
        'MYSQL_ORDER'           : datasetConfig.get('MYSQL_ORDER',False),
        'endpointURL'           : akara.module_config().get('endpointURL'),
    }

    proxy = None# @@TODO: Add support for proxies  global_conf.get('sparql_proxy')
    nsBindings = dict([ (k,URIRef(v)) for k,v in akara.module_config().get("nsPrefixes",{}).items()])

    dataStoreOWL = akara.module_config().get('datastore_owl')
    dataStoreOntGraph = Graph()
    if not proxy and datasetConfig.get('type') == 'MySQL':
        litProps.update(OWL.literalProperties)
        litProps.update(RDFS.literalProperties)
        resProps.update(RDFS.resourceProperties)

        litProps.update(
            map(URIRef,akara.module_config().get("sqlLiteralProps",[]))
        )
        resProps.update(
            map(URIRef,akara.module_config().get("sqlResourceProps",[]))
        )

        if dataStoreOWL:
            for dsOwl in dataStoreOWL.split(','):
                dataStoreOntGraph.parse(dsOwl)

            for litProp,resProp in dataStoreOntGraph.query(OWL_PROPERTIES_QUERY,
                initNs={u'owl':OWL_NS}):
                if litProp:
                    litProps.add(litProp)
                if resProp:
                    #Need to account for OWL Full, where datatype properties
                    #can be IFPs
                    if (resProp,
                        RDF.type,
                        OWL.DatatypeProperty) not in dataStoreOntGraph:
                        resProps.add(resProp)
        else:
            triclopsConf['datastore_owl'] = 'N/A'
        print "Registered %s owl:DatatypeProperties"%len(litProps)
        print "Registered %s owl:ObjectProperties"%len(resProps)

        if False:# @@TODO support for SPARQL RIF Core entailment global_conf.get('topDownEntailment',False):
            pass
#            from FuXi.DLP.DLNormalization import NormalFormReduction
#            from FuXi.DLP import DisjunctiveNormalForm
#            from FuXi.Horn.HornRules import HornFromDL, HornFromN3, Ruleset
#            from FuXi.Syntax.InfixOWL import *
#            from FuXi.Horn import DATALOG_SAFETY_STRICT
#            from FuXi.Rete.Magic import IdentifyDerivedPredicates
#            complementExpanded =[]
#            _ruleSet = Ruleset()
#            if global_conf.get('SkipComplementExpansion'):
#                for kvStr in global_conf.get('SkipComplementExpansion').split('|') :
#                    pref,uri=kvStr.split(':')
#                    complementExpanded.append(URIRef(nsBindings[pref]+uri))
#
#            definingOntology = global_conf.get('entailment_owl')
#            for ont in definingOntology.split(','):
#                if os.path.exists(ont):
#                    ontGraphPath = OsPathToUri(ont)
#                else:
#                    ontGraphPath = ont
#                print >>sys.stderr, "Parsing Semantic Web root Graph.. ", ontGraphPath
#                for owlImport in ontGraph.parse(ontGraphPath).objects(predicate=OWL_NS.imports):
#                    ontGraph.parse(owlImport)
#                    print >>sys.stderr, "Parsed Semantic Web Graph.. ", owlImport
#
#            for prefix,uri in nsBindings.items():
#                ontGraph.bind(prefix,uri)
#
#            builtins = global_conf.get('builtins')
#            if global_conf.get('entailment_n3'):
#                #setup rules / builtins
#                if builtins:
#                    import imp
#                    userFuncs = imp.load_source('builtins', builtins)
#                    rs = HornFromN3(global_conf.get('entailment_n3'),
#                        additionalBuiltins=userFuncs.ADDITIONAL_FILTERS)
#                else:
#                    rs = HornFromN3(global_conf.get('entailment_n3'))
#                print "Parsed %s rules from %s"%(len(rs.formulae),global_conf.get('entailment_n3'))
#                _ruleSet.formulae.extend(rs)
#
#            #Setup builtin template graph
#            builtinTemplates   = global_conf.get('builtinTemplates',False)
#            if builtinTemplates:
#                builtinTemplateGraph.parse(builtinTemplates,format='n3')
#                #setup ddl graph
#            ddlGraph = global_conf.get('ddlGraph')
#            if ddlGraph:
#                ddlGraph = Graph().parse(ddlGraph,
#                    format='n3')
#                print "Registering DDL metadata"
#                defaultDerivedPreds.extend(
#                    IdentifyDerivedPredicates(
#                        ddlGraph,
#                        ontGraph,
#                        _ruleSet))
#                #Reduce the DL expressions to a normal form
#            NormalFormReduction(ontGraph)
#            #extract rules form normalized ontology graph
#            dlp=HornFromDL(ontGraph,
#                derivedPreds=defaultDerivedPreds,
#                complSkip=complementExpansion(ontGraph))
#            _ruleSet.formulae.extend(dlp)
#            #normalize the ruleset
#            ruleSet.formulae.extend(set(DisjunctiveNormalForm(_ruleSet,safety=DATALOG_SAFETY_STRICT)))
    return triclopsConf

def ReplaceGraph(datasetOrName,
                 graphUri,
                 srcStream,
                 format='xml',
                 storeName=True,
                 baseUri=None,
                 smartDiff=False,
                 debug=False):
    #TODO: do a lazy replace (only the diff - ala 4Suite repository)
    store = ConnectToDataset(datasetOrName) if storeName else datasetOrName
    g = Graph(store, graphUri)
    if smartDiff:
        def hasBNodes(triple):
            return filter(lambda term:isinstance(term,BNode),triple)
        new_graph = Graph().parse(srcStream,publicID=baseUri)
        stmsToAdd = [ s for s in new_graph
                        if s not in g or hasBNodes(s) ]
        stmsToDel = [ s for s in g
                        if s not in new_graph or hasBNodes(s) ]
        for s in stmsToDel:
            g.remove(s)
        for s in stmsToAdd:
            g.add(s)
        if debug:
            print "Removed %s triples and added %s from/to %s"%(
                len(stmsToDel),
                len(stmsToAdd),
                graphUri
            )
    else:
        g.remove((None, None, None))
        g.parse(srcStream,publicID=baseUri)
    store.commit()

def ClearGraph(datasetOrName,graphUri,storeName=True):
    #TODO: do a lazy replace (only the diff - ala 4Suite repository)
    store = ConnectToDataset(datasetOrName) if storeName else datasetOrName
    g = Graph(store, graphUri)
    g.remove((None, None, None))
    store.commit()

def DestroyOrCreateDataset(datasetName):
    """
    Initialize dataset (if exists) or create it if it doesn't
    """
    datasetConfig = akara.module_config().get(datasetName)
    assert datasetConfig is not None, datasetName
    if datasetConfig['type'] == 'MySQL':
        configStr = 'user=%s,password=%s,db=%s,port=%s,host=%s' % (
            datasetConfig.get('mysqluser'),
            datasetConfig.get('mysqlpw'),
            datasetConfig.get('mysqldb'),
            datasetConfig.get('mysqlPort',3306),
            datasetConfig.get('mysqlhost')
            )
        store = plugin.get('MySQL', Store)(datasetConfig.get('mysqlStoreId'))
        rt = store.open(configStr,create=False)
        if rt == NO_STORE:
            store.open(configStr,create=True)
        else:
            store.destroy(configStr)
            store.open(configStr,create=True)
        return store
    else:
        raise NotImplementedError("Only dataset supported by Akamu is MySQL")


def ConnectToDataset(datasetName):
    """
    Return rdflib store corresponding to the named dataset, whose connection
    parameters are specified in the configuration file
    """
    datasetConfig = akara.module_config().get(datasetName)
    assert datasetConfig is not None
    if datasetConfig['type'] == 'MySQL':
        configStr = 'user=%s,password=%s,db=%s,port=%s,host=%s' % (
            datasetConfig.get('mysqluser'),
            datasetConfig.get('mysqlpw'),
            datasetConfig.get('mysqldb'),
            datasetConfig.get('mysqlPort',3306),
            datasetConfig.get('mysqlhost')
        )
        store = plugin.get('MySQL', Store)(datasetConfig.get('mysqlStoreId'))
        store.open(configStr, create=False)
        store.literal_properties.update(
            map(URIRef,akara.module_config().get("sqlLiteralProps",[]))
        )
        store.resource_properties.update(
            map(URIRef,akara.module_config().get("sqlResourceProps",[]))
        )
        return store
    elif datasetConfig['type'] == 'SPARQLService':
        if 'endpoint' not in datasetConfig:
            raise SyntaxError('Missing "endpoint" directive')
        sparql_store = plugin.get('SPARQL', Store)(datasetConfig.get('endpoint'))
        for k,v in datasetConfig.get('extraQueryParams',{}).items():
            sparql_store._querytext.append((k,v))
        sparql_store.method = POST if datasetConfig.get(
            'method','GET').lower() == 'post' else GET
        return sparql_store
    else:
        raise NotImplementedError("Only dataset supported by Akamu is MySQL")

def Ask(queryFile,datasetName,graphUri=None,params=None,debug=False):
    """
    Same as Query but where query is ASK (returns boolean)
    """
    store = ConnectToDataset(datasetName)
    g     = ConjunctiveGraph(store) if graphUri is None else Graph(store,graphUri)
    qFile = os.path.join(akara.module_config().get("sparqlQueryFiles"),queryFile)
    query = open(qFile).read()
    query = query if params is None else query % params
    if debug:
        print query
    initNs = dict([ (k,URIRef(v)) for k,v in akara.module_config().get("nsPrefixes",{}).items()])
    if debug:
        then = time.time()
        rt = g.query(query,initNs=initNs,DEBUG=debug).serialize(format='python')
        print "Query time", time.time() - then
    else:
        rt = g.query(query,initNs=initNs,DEBUG=debug).serialize(format='python')
    return rt

def Query(queryFile,datasetName,graphUri=None,params=None,debug=False):
    """
    Evaluate a query (stored in a SPARQL file in the location indicated in the
    configuration) against the given dataset (and optional named graph within it)
    using the optional parameters given
    """
    store = ConnectToDataset(datasetName)
    g     = ConjunctiveGraph(store) if graphUri is None else Graph(store,graphUri)
    qFile = os.path.join(akara.module_config().get("sparqlQueryFiles"),queryFile)
    query = open(qFile).read()
    query = query if params is None else query % params
    if debug:
        print query
    initNs = dict([ (k,URIRef(v)) for k,v in akara.module_config().get("nsPrefixes",{}).items()])
    for rt in g.query(
        query,
        initNs=initNs,
        DEBUG=debug):
        yield rt

def GetParameterizedQuery(queryFile,params=None):
    qFile = os.path.join(akara.module_config().get("sparqlQueryFiles"),queryFile)
    query = open(qFile).read()
    return query if params is None else query % params