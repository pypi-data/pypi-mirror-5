#ifndef DBCONTROLLER_H
#define DBCONTROLLER_H

#include <map>
#include <vector>
#include <string>
#include "filterdefs.h"
#include "streammanager.h"
#include "controller.h"

class FileInputOutputStream;
class FileInputStream;
class BSONObj;
class BSONArrayObj;
class Command;
class Logger;
class FilterParser;
class Index;
class IndexAlgorithm;

class DBController: public Controller
{
    public:
        DBController();
        virtual ~DBController();

        void initialize();
        void initialize(std::string dataDir);
        void shutdown();

        const BSONObj* insert(const char* db, const char* ns, BSONObj* bson, const BSONObj* options = NULL);
		  bool dropNamespace(const char* db, const char* ns, const BSONObj* options = NULL);
        void update(const char* db, const char* ns, BSONObj* bson, const BSONObj* options = NULL);
        void remove(const char* db, const char* ns, const char* documentId, const char* revision, const BSONObj* options = NULL);
        BSONArrayObj* find(const char* db, const char* ns, const char* select, const char* filter, const BSONObj* options = NULL) throw (ParseException);
        BSONObj* findFirst(const char* db, const char* ns, const char* select, const char* filter, const BSONObj* options = NULL) throw (ParseException);
        BSONObj* readBSON(StreamType* stream);
		  std::vector<std::string>* dbs(const BSONObj* options = NULL) const;
		  std::vector<std::string>* namespaces(const char* db, const BSONObj* options = NULL) const;

		  static void fillRequiredFields(BSONObj* bson);
	 protected:

    private:
		  Logger* _logger;
		  bool _initialized;
		  std::string _dataDir;

	 private:
		  BSONArrayObj* findFullScan(const char* db, const char* ns, const char* select, FilterParser* parser, const BSONObj* options) throw (ParseException);
		  void clearCache();
		  long checkStructure(BSONObj* bson);
		  Index* findIndex(const char* db, const char* ns, BSONObj* bson);
		  void insertIndex(const char* db, const char* ns, BSONObj* bson, long filePos);
		  void updateIndex(const char* db, const char* ns, BSONObj* bson, long filePos);
		  void writeBSON(StreamType* stream, BSONObj* obj);
		  void migrateIndex0_3(const char* db, const char* ns, InputStream* stream, IndexAlgorithm* impl);
};

#endif // DBCONTROLLER_H
