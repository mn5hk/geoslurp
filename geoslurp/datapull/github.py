# This file is part of geoslurp.
# geoslurp is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# geoslurp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (roelof@geod.uni-bonn.de), 2018
import re
import os
import json
from geoslurp.datapull import CrawlerBase
from geoslurp.datapull.http import Uri as http

class GithubFilter():
    """Filter used for testing a certain dict element"""
    def __init__(self,regexdict={"type":"blob"}):
        self.regexes={}
        for ky,regex in regexdict.items():
            self.regexes[ky]=re.compile(regex)

    def isValid(self,elem):
        """Returns True if all of the regex criteria match the elem"""
        valid=True
        for ky,regex in self.regexes.items():
            if not regex.search(elem[ky]):
                valid= False

        return valid





class Crawler(CrawlerBase):
    """Crawls a github repository fixed to a certain commit"""
    def __init__(self, reponame,commitsha=None,filter=GithubFilter(),followfilt=GithubFilter({"type":"tree"}),oauthtoken=None):
        #construct the catalog url
        catalogurl="https://api.github.com/repos/"+reponame+"/git/trees/"+commitsha
        super().__init__(catalogurl)
        self.filter=filter
        self.followFilter=followfilt
        self.repo=reponame
        self.token=oauthtoken

    def getSubTree(self,url):
        if self.token:
            #add the api token to the end
            url+="?access_token=%s"%(self.token)
        return json.loads(http(url).buffer().getvalue())

    def uris(self,depth=10):
        """retrieve all """
        pass
        #add an additional elemet to keep track of the fullpath
        # for elem in self.treeitems(depth=depth):
        #     print(os.path.join(elem["dirpath"],elem['path']),elem['url'])



    def treeitems(self,rootelem=None,depth=10,dirpath=None):
        """ generator which recursively list all elements in a git tree"""


        if depth == 0:
            # signals a stopiteration
            return
        else:
            depth-=1

        #set rootelem and dirpath upon first entry
        if not rootelem:
            rootelem=self.getSubTree(url=self.rooturl)

        if not dirpath:
            dirpath=self.repo

        for treelem in rootelem['tree']:

            if self.filter.isValid(treelem):
                treelem["dirpath"]=dirpath
                #modify url to link to a arw github file

                treelem['url']="https://github.com/"+self.repo+"/raw/master/"+treelem['dirpath'].lstrip(self.repo)+"/"+treelem["path"]
                yield treelem
                continue

            if self.followFilter.isValid(treelem):
                #recurse through subtree
                subtree=self.getSubTree(treelem["url"])
                yield from self.treeitems(subtree,depth,os.path.join(dirpath,treelem["path"]))
