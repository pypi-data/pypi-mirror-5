from pyhammer.tasks.taskbase import TaskBase
from pyhammer.utils import execProg

class SvnCommitTask(TaskBase):
    def __init__( self, dir, add = True, user = None, pwd = None ):
        super().__init__()
        
        self.__dir = dir
        self.__add = add
        self.__user = user
        self.__pwd = pwd

    def do( self ):
        items = []
        if type(self.__dir) is str:
            items.append(self.__dir)
        else:
            items = self.__dir

        for i, item in enumerate( items ):
            if not self.process(item):
                return False
        return True

    def process(self, item):
        self.reporter.message( "COMMIT: %s" % item )
        addResult = True
        if self.__add:
            command = "svn add --force *.*"
            addResult = execProg( command, self.reporter, item ) == 0

        if addResult :
            commitMessage = "Commited by Build"
            command = "svn commit -m \"%s\"" % commitMessage

            if self.__user:
                command += " --username %s --password %s" % (self.__user, self.__pwd)
            self.reporter.message( "SVN COMMIT DIR: %s" % item )
            return execProg( command, self.reporter, item ) == 0
        return False