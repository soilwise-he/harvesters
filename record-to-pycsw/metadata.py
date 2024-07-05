
from pycsw.core import config as pconfig
from pycsw.core import metadata, repository, util
from pycsw.core.etree import etree
from pycsw.core.etree import PARSER
from pycsw.core.util import parse_ini_config


# todo: dublin core parser for json, maybe even use rdflib, ask tom



context = pconfig.StaticContext()

database = os.getenviron('db')
table = os.getenviron('table') or 'records'

repo = repository.Repository(database, context, table=table)

# get records to be imported from db (updated after xxx?) or "where id not in (select id from records)"

total = len(recs)
    counter = 0

    for recfile in sorted(recs):
        counter += 1
        metadata_record = None
        LOGGER.info('Processing record %s (%d of %d)', recfile, counter, total)

        # if record is rdf (openaire, esdac, ...)
        # import using rdflib
        # serialise as rdf-xml
        # parse as {rdf}DC


        # read document
        try:
            metadata_record = json.load(recfile) 
        except json.decoder.JSONDecodeError as err:
            metadata_record = etree.parse(recfile, context.parser)
        except etree.XMLSyntaxError as err:
            LOGGER.error('XML document "%s" is not well-formed', recfile, exc_info=True)
            continue
        except Exception as err:
            LOGGER.exception('XML document "%s" is not well-formed', recfile)
            continue

        try:
            record = metadata.parse_record(context, metadata_record, repo)
        except Exception as err:
            LOGGER.exception('Could not parse "%s" as an XML record', recfile)
            continue

        for rec in record:
            LOGGER.info('Inserting %s %s into database %s, table %s ....',
                        rec.typename, rec.identifier, database, table)

            # TODO: do this as CSW Harvest
            try:
                repo.insert(rec, 'local', util.get_today_and_now())
                loaded_files.add(recfile)
                LOGGER.info('Inserted %s', recfile)
            except Exception as err:
                if force_update:
                    LOGGER.info('Record exists. Updating.')
                    repo.update(rec)
                    LOGGER.info('Updated %s', recfile)
                    loaded_files.add(recfile)
                else:
                    if isinstance(err, DBAPIError) and err.args:
                        # Pull a decent database error message and not the full SQL that was run
                        # since INSERT SQL statements are rather large.
                        LOGGER.error('ERROR: %s not inserted: %s', recfile, err.args[0], exc_info=True)
                    else:
                        LOGGER.error('ERROR: %s not inserted: %s', recfile, err, exc_info=True)

    return tuple(loaded_files)