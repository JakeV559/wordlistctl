#!/usr/bin/env python3
# -*- coding: latin-1 -*- ######################################################
#                                                                              #
# wordlistctl - Fetch, install and search wordlist archives from websites and  #
# torrent peers.                                                               #
#                                                                              #
# DESCRIPTION                                                                  #
# Script to fetch, install, update and search wordlist archives from websites  #
# offering wordlists with more than 2900 wordlists available.                  #
#                                                                              #
# AUTHORS                                                                      #
# sepehrdad.dev@gmail.com                                                      #
################################################################################


__author__ = "Sepehrdad Sh"
__organization__ = "blackarch.org"
__license__ = "GPLv3"
__version__ = "0.8.1-beta"
__project__ = "wordlistctl"

__wordlist_path__ = "/usr/share/wordlists"
__category__ = ""
__config__ = {}
__decompress__ = False
__remove__ = False
__prefer_http__ = False
__torrent_dl__ = True

__executer__ = None
__max_parallel__ = 5
__session__ = None
__useragent__ = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20180101 Firefox/65.0"
__proxy__ = {}
__proxy_http__ = False
__proxy_torrent__ = False
__chunk_size__ = 1024
__errored__ = {}
__no_confirm__ = False
__no_integrity_check__ = False
__use_process_pool__ = False


def err(string):
    print(colored("[-]", "red", attrs=["bold"]) +
          " {0}".format(string), file=sys.stderr)


def warn(string):
    print(colored("[!]", "yellow", attrs=["bold"]) + " {0}".format(string))


def info(string):
    print(colored("[*]", "blue", attrs=["bold"]) + " {0}".format(string))


def success(string):
    print(colored("[+]", "green", attrs=["bold"]) + " {0}".format(string))


def ask(question):
    global __no_confirm__
    print(colored("[?]", "blue", attrs=["bold"]) +
          " {0}".format(question), end='')
    if __no_confirm__:
        return ''
    return input()


def usage():
    __usage__ = "usage:\n\n"
    __usage__ += "  {0} -f <arg> [options] | -s <arg> [options] | -S <arg> | <misc>\n\n"
    __usage__ += "options:\n\n"
    __usage__ += "  -f <num>   - download chosen wordlist - ? to list wordlists with id\n"
    __usage__ += "  -d <dir>   - wordlists base directory (default: {1})\n"
    __usage__ += "  -c <num>   - change wordlists category - ? to list wordlists categories\n"
    __usage__ += "  -s <regex> - wordlist to search using <regex> in base directory\n"
    __usage__ += "  -S <regex> - wordlist to search using <regex> in sites\n"
    __usage__ += "  -h         - prefer http\n"
    __usage__ += "  -X         - decompress wordlist\n"
    __usage__ += "  -F <str>   - list wordlists in categories given\n"
    __usage__ += "  -r         - remove compressed file after decompression\n"
    __usage__ += "  -t <num>   - max parallel downloads (default: {0})\n\n".format(
        __max_parallel__)
    __usage__ += "misc:\n\n"
    __usage__ += "  -C         - disable terminal colors\n"
    __usage__ += "  -T         - disable torrent download\n"
    __usage__ += "  -P         - set proxy (format: proto://user:pass@host:port)\n"
    __usage__ += "  -A         - set useragent string\n"
    __usage__ += "  -Y         - proxy http\n"
    __usage__ += "  -Z         - proxy torrent\n"
    __usage__ += "  -M         - use multiprocessing for parallelization\n"
    __usage__ += "  -N         - do not ask for any confirmation\n"
    __usage__ += "  -I         - do not check for integrity\n"
    __usage__ += "  -V         - print version of wordlistctl and exit\n"
    __usage__ += "  -H         - print this help and exit\n\n"
    __usage__ += "example:\n\n"
    __usage__ += "  # download and decompress all wordlists and remove archive\n"
    __usage__ += "  $ wordlistctl -f 0 -Xr\n\n"
    __usage__ += "  # download all wordlists in username category\n"
    __usage__ += "  $ wordlistctl -f 0 -c 0\n\n"
    __usage__ += "  # list all wordlists in password category with id\n"
    __usage__ += "  $ wordlistctl -f ? -c 1\n\n"
    __usage__ += "  # download and decompress all wordlists in misc category\n"
    __usage__ += "  $ wordlistctl -f 0 -c 4 -X\n\n"
    __usage__ += "  # download all wordlists in filename category using 20 threads\n"
    __usage__ += "  $ wordlistctl -c 3 -f 0 -t 20\n\n"
    __usage__ += "  # download wordlist with id 2 to \"~/wordlists\" directory using http\n"
    __usage__ += "  $ wordlistctl -f 2 -d ~/wordlists -h\n\n"
    __usage__ += "  # print wordlists in username and password categories\n"
    __usage__ += "  $ wordlistctl -F username,password\n\n"
    __usage__ += "  # download all wordlists with using tor socks5 proxy\n"
    __usage__ += "  $ wordlistctl -f 0 -P \"socks5://127.0.0.1:9050\" -Y\n\n"
    __usage__ += "  # download all wordlists with using http proxy and noleak useragent\n"
    __usage__ += "  $ wordlistctl -f 0 -P \"http://127.0.0.1:9060\" -Y -A \"noleak\"\n"

    print(__usage__.format(__project__, __wordlist_path__))


def version():
    __str_version__ = "{0} v{1}".format(__project__, __version__)
    print(__str_version__)


def banner():
    __str_banner__ = "--==[ {0} by {1} ]==--\n".format(
        __project__, __organization__)
    print(colored(__str_banner__, "red", attrs=["bold"]))


def decompress_gbl(infilename):
    filename = os.path.basename(infilename)
    try:
        infile = None
        __outfile__ = os.path.splitext(infilename)[0]
        if os.path.isfile(__outfile__):
            warn("{0} already exists -- skipping".format(os.path.basename(__outfile__)))
        else:
            if re.fullmatch(r"^.*\.(gz)$", infilename.lower()):
                infile = gzip.GzipFile(infilename, "rb")
            elif re.fullmatch(r"^.*\.(bz|bz2)$", infilename.lower()):
                infile = bz2.BZ2File(infilename, "rb")
            elif re.fullmatch(r"^.*\.(lzma|xz)$", infilename.lower()):
                infile = lzma.LZMAFile(infilename, "rb")
            else:
                raise ValueError("unknown file type")
            info("decompressing {0}".format(filename))
            outfile = open(__outfile__, "wb")
            copyfileobj(infile, outfile)
            outfile.close()
            success("decompressing {0} completed".format(filename))
        return True
    except Exception as ex:
        err("Error while decompressing {0}: {1}".format(filename, str(ex)))
        remove(infilename)
        return False


def decompress_archive(infilename):
    filename = os.path.basename(infilename)
    try:
        os.chdir(os.path.dirname(infilename))
        info("decompressing {0}".format(filename))
        if re.fullmatch(r"^.*\.(rar)$", filename.lower()):
            infile = rarfile.RarFile(infilename)
            infile.extractall()
        else:
            libarchive.extract_file(infilename)
        success("decompressing {0} completed".format(filename))
        return True
    except Exception as ex:
        err("Error while decompressing {0}: {1}".format(filename, str(ex)))
        remove(infilename)
        return False


def decompress(infilename):
    filename = os.path.basename(infilename)

    if not __decompress__:
        return True
    try:
        if re.fullmatch(r"^.*\.(rar|zip|7z|tar|tar.gz|tar.xz|tar.bz2)$", filename.lower()):
            decompress_archive(infilename)
        elif re.fullmatch(r"^.*\.(gz|bz|bz2|lzma)$", filename.lower()):
            decompress_gbl(infilename)
        else:
            return True
        clean(infilename)
        return True
    except Exception as ex:
        err("Error while decompressing {0}: {1}".format(filename, str(ex)))
        remove(infilename)
        return False


def clean(filename):
    if __remove__:
        remove(filename)


def remove(filename):
    try:
        os.remove(filename)
    except:
        pass


def resolve_mediafire(url):
    resolved = ""
    try:
        page = requests.head(
            url, headers={"User-Agent": ""}, allow_redirects=True)
        if page.url != url:
            resolved = page.url
        else:
            page = requests.get(url, headers={"User-Agent": ""})
            html = BeautifulSoup(page.text, "html.parser")
            for i in html.find_all('a', {"class": "input"}):
                if str(i.text).strip().startswith("Download ("):
                    resolved = i["href"]
    except:
        pass
    finally:
        return resolved


def resolve_sourceforge(url):
    resolved = ""
    try:
        rq = requests.get(url, stream=True,
                          headers={"User-Agent": ""},
                          allow_redirects=True)
        resolved = rq.url
    except:
        pass
    finally:
        return resolved


def resolve(url):
    resolver = None
    resolved = ""
    if str(url).startswith("http://downloads.sourceforge.net/"):
        resolver = resolve_sourceforge
    elif str(url).startswith("http://www.mediafire.com/file/"):
        resolver = resolve_mediafire
    if resolver is None:
        resolved = url
    else:
        count = 0
        while (resolved == "") and (count < 10):
            resolved = resolver(url)
            time.sleep(10)
            count += 1
    return resolved


def to_readable_size(size):
    units = {0: 'bytes',
             1: 'Kbytes',
             2: 'Mbytes',
             3: 'Gbytes',
             4: 'Tbytes'}
    i = 0
    while size > 1000:
        size = size / 1000
        i += 1
    return "{0:.2f} {1}".format(size, units[i])


def torrent_setup_proxy():
    global __session__
    global __proxy__

    if __session__ is None:
        err("session not initialized")
        exit(-1)
    elif __proxy__ == {}:
        err("proxy is empty")
        exit(-1)
    elif not __proxy_torrent__:
        return
    regex = r"^(http|https|socks4|socks5)://([a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@)?[a-z0-9.]+:[0-9]{1,5}$"
    if re.match(regex, str(__proxy__['http']).lower()):
        username, password, host, port = "", "", "", ""
        proxy = str(__proxy__['http'])
        proxy_settings = libtorrent.proxy_settings()
        proto = proxy.split("://")[0]
        proxy = proxy.replace("{0}://".format(proto), "")
        if proxy.__contains__('@'):
            creds = proxy.split('@')[0]
            username, password = creds.split(':')
            proxy_settings.username, proxy_settings.password = username, password
            proxy = proxy.replace("{0}@".format(creds), "")
        host, port = proxy.split(':')
        proxy_settings.proxy_hostnames = True
        proxy_settings.proxy_peer_connections = True
        proxy_settings.hostname = host
        proxy_settings.proxy_port = port
        if username != "" and password != "":
            if proto in ("http", "https"):
                proxy_settings.proxy_type = libtorrent.proxy_type().http_pw
            elif proto in ("socks4", "socks5"):
                proxy_settings.proxy_type = libtorrent.proxy_type().socks5_pw
        else:
            if proto in ("http", "https"):
                proxy_settings.proxy_type = libtorrent.proxy_type().http
            elif proto in ("socks4", "socks5"):
                proxy_settings.proxy_type = libtorrent.proxy_type().socks5
        __session__.set_dht_proxy(proxy_settings)
        __session__.set_peer_proxy(proxy_settings)
        __session__.set_tracker_proxy(proxy_settings)
        __session__.set_web_seed_proxy(proxy_settings)
        __session__.set_proxy(proxy_settings)
        settings = __session__.settings()
        settings.force_proxy = True
        settings.proxy_hostnames = True
        settings.proxy_peer_connections = True
        settings.proxy_tracker_connections = True
        settings.anonymous_mode = True
        __session__.dht_proxy()
        __session__.peer_proxy()
        __session__.tracker_proxy()
        __session__.web_seed_proxy()
        __session__.proxy()
        __session__.set_settings(settings)
    else:
        err("invalid proxy format")
        exit(-1)


def integrity_check(checksum, path):
    global __chunk_size__
    global __no_integrity_check__
    filename = os.path.basename(path)
    info("checking {0} integrity".format(filename))
    if checksum == 'SKIP' or __no_integrity_check__:
        warn("{0} integrity check -- skipping".format(filename))
        return True
    hashagent = md5()
    fp = open(path, 'rb')
    while True:
        data = fp.read(__chunk_size__)
        if not data:
            break
        hashagent.update(data)
    if checksum != hashagent.hexdigest():
        err("{0} integrity check -- failed".format(filename))
        return False
    else:
        success("{0} integrity check -- passed".format(filename))
        return True


def fetch_file(url, path, checksum):
    global __proxy__
    global __proxy_http__
    global __chunk_size__
    proxy = {}
    if __proxy_http__:
        proxy = __proxy__
    filename = os.path.basename(path)
    try:
        if check_file(path):
            warn("{0} already exists -- skipping".format(filename))
        else:
            info("downloading {0} to {1}".format(filename, path))
            dlurl = resolve(url)
            rq = requests.get(dlurl, stream=True,
                              headers={"User-Agent": __useragent__},
                              proxies=proxy)
            fp = open(path, "wb")
            for data in rq.iter_content(chunk_size=__chunk_size__):
                fp.write(data)
            fp.close()
            success("downloading {0} completed".format(filename))
        if (not integrity_check(checksum, path)) or (not decompress(path)):
            raise IOError()
        return True
    except KeyboardInterrupt:
        return True
    except Exception as ex:
        str_ex = str(ex)
        if str_ex.__len__() > 0:
            str_ex = ": " + str_ex
        err("Error while downloading {0}{1}".format(url, str_ex))
        remove(path)
        return False


def fetch_torrent(url, path):
    global __session__
    global __proxy__
    global __torrent_dl__
    if __session__ is None:
        __session__ = libtorrent.session({"listen_interfaces": "0.0.0.0:6881"})
        if __proxy__ != {}:
            torrent_setup_proxy()
        __session__.start_dht()
    magnet = False
    if str(url).startswith("magnet:?"):
        magnet = True
    handle = None
    try:

        if magnet:
            handle = libtorrent.add_magnet_uri(__session__, url,
                                               {
                                                   "save_path": os.path.dirname(path),
                                                   "storage_mode": libtorrent.storage_mode_t(2),
                                                   "paused": False,
                                                   "auto_managed": True,
                                                   "duplicate_is_error": True
                                               }
                                               )
            info("downloading metadata\n")
            while not handle.has_metadata():
                time.sleep(0.1)
            success("downloaded metadata")
        else:

            if not __torrent_dl__:
                return True
            if os.path.isfile(path):
                handle = __session__.add_torrent(
                    {"ti": libtorrent.torrent_info(path), "save_path": os.path.dirname(path)})
                remove(path)
            else:
                err("{0} not found".format(path))
                exit(-1)
        __outfilename__ = "{0}/{1}".format(
            os.path.dirname(path), handle.name())
        info("downloading {0} to {1}".format(handle.name(), __outfilename__))
        while not handle.is_seed():
            time.sleep(0.1)
        __session__.remove_torrent(handle)
        success("downloading {0} completed".format(handle.name()))
        if not decompress(__outfilename__):
            raise IOError()
        return True
    except KeyboardInterrupt:
        return True
    except Exception as ex:
        str_ex = str(ex)
        if str_ex.__len__() > 0:
            str_ex = ": " + str_ex
        err("Error while downloading {0}{1}".format(url, str_ex))
        remove(path)
        return False


def download_wordlist(config, wordlistname, category):
    global __errored__
    __filename__ = ""
    __file_directory__ = ""
    __file_path__ = ""
    check_dir("{0}/{1}".format(__wordlist_path__, category))
    __file_directory__ = "{0}/{1}".format(__wordlist_path__, category)
    res = True
    try:
        urls = config["url"]
        urls.sort()
        url = None
        if __prefer_http__:
            url = urls[0]
        else:
            url = urls[-1]
        __filename__ = url.split('/')[-1]
        __file_path__ = "{0}/{1}".format(__file_directory__, __filename__)
        __csum__ = config["sum"][config["url"].index(url)]
        if url.startswith("http"):
            res = fetch_file(url, __file_path__, __csum__)
        else:
            res = fetch_file(url.replace("torrent+", ""),
                             __file_path__, __csum__)
            if not res:
                raise IOError()
            res = fetch_torrent(url, __file_path__)

        if not res:
            raise IOError()

    except Exception as ex:
        str_ex = str(ex)
        if str_ex.__len__() > 0:
            str_ex = ": " + str_ex
        err("Error while downloading {0}{1}".format(wordlistname, str_ex))
        __errored__[category]["files"].append(config)
        return -1


def download_wordlists(code):
    global __config__
    global __executer__
    __wordlist_id__ = 0

    check_dir(__wordlist_path__)

    __wordlist_id__ = to_int(code)
    __wordlists_count__ = 0
    for i in __config__.keys():
        __wordlists_count__ += __config__[i]["count"]

    lst = {}

    try:
        if (__wordlist_id__ >= __wordlists_count__ + 1) or __wordlist_id__ < 0:
            raise IndexError("{0} is not a valid wordlist id".format(code))
        elif __wordlist_id__ == 0:
            if __category__ == "":
                lst = __config__
            else:
                lst[__category__] = __config__[__category__]
        elif __category__ != "":
            lst[__category__] = {"files": [__config__[
                __category__]["files"][__wordlist_id__ - 1]]}
        else:
            cat = ""
            count = 0
            wid = 0
            for i in __config__.keys():
                count += __config__[i]["count"]
                if (__wordlist_id__ - 1) < (count):
                    cat = i
                    break
            wid = (__wordlist_id__ - 1) - count
            lst[cat] = {"files": [__config__[cat]["files"][wid]]}
        for i in lst.keys():
            for j in lst[i]["files"]:
                __executer__.submit(download_wordlist, j, j["name"], i)
        __executer__.shutdown(wait=True)
        errored = 0
        for i in __errored__.keys():
            errored += __errored__[i]["files"].__len__()
        if errored > 0:
            ans = ask(
                "Some wordlists were not downloaded would you like to redownload? [y/N]")
            if ans.lower() == 'n' or ans.lower() == '':
                return 0
            elif ans.lower() != 'y':
                err("invalid answer")
                exit(-1)
            redownload()
    except Exception as ex:
        err("Error unable to download wordlist: {0}".format(str(ex)))
        return -1
    return 0


def redownload():
    global __errored__
    global __executer__
    global __use_process_pool__
    info("redownloading unsuccessful downloads")
    if __use_process_pool__:
        __executer__ = ProcessPoolExecutor(__max_parallel__)
    else:
        __executer__ = ThreadPoolExecutor(__max_parallel__)
    for i in __errored__.keys():
        for j in __errored__[i]["files"]:
            __executer__.submit(download_wordlist, j, j["name"], i)
    __executer__.shutdown(wait=True)


def print_wordlists(categories=""):
    global __config__
    if categories == "":
        lst = []
        success("available wordlists:")
        print()
        print("    > 0  - all wordlists")
        if __category__ != "":
            lst = __config__[__category__]["files"]
        else:
            for i in __config__.keys():
                lst += __config__[i]["files"]

        for i in lst:
            print("    > {0}  - {1} ({2}, {3})".format(lst.index(i) + 1, i["name"],
                                                       to_readable_size(
                                                           i["size"][0]),
                                                       to_readable_size(i["size"][1])))
        print("")
    else:
        categories_list = set([i.strip() for i in categories.split(',')])
        for i in categories_list:
            if i not in __config__.keys():
                err("category {0} is unavailable".format(i))
                exit(-1)
        for i in categories_list:
            success("{0}:".format(i))
            for j in __config__[i]["files"]:
                print("    > {0} ({1}, {2})".format(j["name"],
                                                    to_readable_size(
                                                        j["size"][0]),
                                                    to_readable_size(j["size"][1])))
            print("")


def search_dir(regex):
    global __wordlist_path__
    count = 0
    try:
        for root, _, files in os.walk(__wordlist_path__):
            for f in files:
                if re.match(regex, f):
                    info("wordlist found: {0}".format(os.path.join(root, f)))
                    count += 1
        if count == 0:
            err("wordlist not found")
    except:
        pass


def search_sites(regex):
    count = 0
    lst = []
    info("searching for {0} in config.json\n".format(regex))
    try:
        if __category__ != "":
            lst = __config__[__category__]["files"]
        else:
            for i in __config__.keys():
                lst += __config__[i]["files"]

        for i in lst:
            if re.match(regex, i["name"]):
                success("wordlist {0} found: id={1}".format(
                    i["name"], lst.index(i) + 1))
                count += 1

        if count == 0:
            err("no wordlist found")
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        err("Error while searching: {0}".format(str(ex)))
        return -1


def check_dir(dir_name):
    try:
        if os.path.isdir(dir_name):
            pass
        else:
            info("creating directory {0}".format(dir_name))
            os.mkdir(dir_name)
    except Exception as ex:
        err("unable to create directory: {0}".format(str(ex)))
        exit(-1)


def check_file(path):
    return os.path.isfile("{0}".format(path))


def check_proxy(proxy):
    try:
        reg = r"^(http|https|socks4|socks5)://([a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@)?[a-z0-9.]+:[0-9]{1,5}$"
        if re.match(reg, proxy['http']):
            return True
        return False
    except Exception as ex:
        err("unable to use proxy: {0}".format(str(ex)))
        exit(-1)


def load_json(infilename):
    try:
        return json.load(open(infilename, 'r'))
    except Exception as ex:
        err("unable to load {0}: {1}".format(infilename, str(ex)))
        return {}


def change_category(code):
    global __category__
    global __config__
    __category_id__ = to_int(code)
    try:
        if (__category_id__ >= list(__config__.keys()).__len__()) or __category_id__ < 0:
            raise IndexError("{0} is not a valid category id".format(code))
        __category__ = list(__config__.keys())[__category_id__]
    except Exception as ex:
        err("Error while changing category: {0}".format(str(ex)))
        exit(-1)


def print_categories():
    index = 0
    success("available wordlists category:")
    print()
    for i in __config__.keys():
        print("    > {0}  - {1} ({2} lsts, {3}, {4})".format(index, i,
                                                             __config__[
                                                                 i]["count"],
                                                             to_readable_size(
                                                                 __config__[i]["size"][0]),
                                                             to_readable_size(__config__[i]["size"][1])))
        index += 1
    print("")


def load_config():
    global __config__
    global __errored__
    configfile = "{0}/config.json".format(
        os.path.dirname(os.path.realpath(__file__)))
    if __config__.__len__() <= 0:
        try:
            if not os.path.isfile(configfile):
                raise FileNotFoundError("Config file not found")
            __config__ = load_json(configfile)
            for i in __config__.keys():
                __errored__[i] = {"files": []}
        except Exception as ex:
            err("Error while loading config files: {0}".format(str(ex)))
            exit(-1)


def to_int(string):
    try:
        return int(string)
    except:
        err("{0} is not a valid number".format(string))
        exit(-1)


def arg_parse(argv):
    global __wordlist_path__
    global __decompress__
    global __remove__
    global __prefer_http__
    global __max_parallel__
    global __torrent_dl__
    global __useragent__
    global __proxy__
    global __proxy_http__
    global __proxy_torrent__
    global __no_confirm__
    global __no_integrity_check__
    global __use_process_pool__
    __operation__ = None
    __arg__ = None
    opFlag = 0

    try:
        opts, _ = getopt.getopt(argv[1:], "MZIYHCNVXThrd:c:f:s:S:t:F:A:P:")

        if opts.__len__() <= 0:
            __operation__ = usage
            return __operation__, None

        for opt, arg in opts:
            if opFlag and re.fullmatch(r"^-([VfsSF])", opt):
                raise getopt.GetoptError("multiple operations selected")
            if opt == "-H":
                __operation__ = usage
                return __operation__, None
            elif opt == "-V":
                __operation__ = version
                opFlag += 1
            elif opt == "-d":
                dirname = os.path.abspath(arg)
                check_dir(dirname)
                __wordlist_path__ = dirname
            elif opt == "-f":
                if arg == '?':
                    __operation__ = print_wordlists
                else:
                    __operation__ = download_wordlists
                    __arg__ = arg
                opFlag += 1
            elif opt == "-s":
                __operation__ = search_dir
                __arg__ = arg
                opFlag += 1
            elif opt == "-X":
                __decompress__ = True
            elif opt == "-r":
                __remove__ = True
            elif opt == "-C":
                os.environ["ANSI_COLORS_DISABLED"] = '1'
            elif opt == "-T":
                __torrent_dl__ = False
            elif opt == "-Z":
                __proxy_torrent__ = True
            elif opt == "-Y":
                __proxy_http__ = True
            elif opt == "-N":
                __no_confirm__ = True
            elif opt == "-I":
                __no_integrity_check__ = True
            elif opt == "-A":
                __useragent__ = arg
            elif opt == "-P":
                if arg.startswith('http://'):
                    proxy = {"http": arg}
                else:
                    proxy = {"http": arg, "https": arg}
                check_proxy(proxy)
                __proxy__ = proxy
            elif opt == "-S":
                __operation__ = search_sites
                __arg__ = arg
                opFlag += 1
            elif opt == "-c":
                if arg == '?':
                    __operation__ = print_categories
                    return __operation__, None
                else:
                    load_config()
                    change_category(arg)
            elif opt == "-h":
                __prefer_http__ = True
            elif opt == "-t":
                __max_parallel__ = to_int(arg)
                if __max_parallel__ <= 0:
                    raise Exception("threads number can't be less than 1")
            elif opt == "-M":
                __use_process_pool__ = True
            elif opt == "-F":
                __operation__ = print_wordlists
                __arg__ = arg
                opFlag += 1
    except getopt.GetoptError as ex:
        err("Error while parsing arguments: {0}".format(str(ex)))
        warn("-H for help and usage")
        exit(-1)
    except Exception as ex:
        err("Error while parsing arguments: {0}".format(str(ex)))
        exit(-1)
    return __operation__, __arg__


def main(argv):
    global __max_parallel__
    global __executer__
    global __use_process_pool__
    banner()

    __operation__, __arg__ = arg_parse(argv)

    try:
        if __operation__ not in [version, usage]:
            load_config()
        if __executer__ is None:
            if __use_process_pool__:
                __executer__ = ProcessPoolExecutor(__max_parallel__)
            else:
                __executer__ = ThreadPoolExecutor(__max_parallel__)
        if __operation__ is not None:
            if __arg__ is not None:
                __operation__(__arg__)
            else:
                __operation__()
        else:
            raise getopt.GetoptError("no operation selected")
        return 0
    except getopt.GetoptError as ex:
        err("Error while running operation: {0}".format(str(ex)))
        warn("-H for help and usage")
        return -1
    except Exception as ex:
        err("Error while running operation: {0}".format(str(ex)))
        return -1


if __name__ == "__main__":
    try:
        import sys
        import os
        import getopt
        import requests
        import re
        import libtorrent
        import libarchive
        import time
        import gzip
        import bz2
        import lzma
        import rarfile
        import json
        from hashlib import md5
        from shutil import copyfileobj
        from bs4 import BeautifulSoup
        from termcolor import colored
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import ProcessPoolExecutor
    except Exception as ex:
        err("Error while loading dependencies: {0}".format(str(ex)))
        exit(-1)

    sys.exit(main(sys.argv))
