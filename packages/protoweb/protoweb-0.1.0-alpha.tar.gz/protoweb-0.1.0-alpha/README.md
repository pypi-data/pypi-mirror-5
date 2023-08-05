# protoweb

**WARNING: ````protoweb```` is in very early stages of development!**

```protoweb``` is a very singular console command that helps you prototype [Cyclone](http://cyclone.io/) based web applications, without the need of focusing too much on server-side when templating and stuff is needed.

*Quick history:* I am very, very systematic when develop things, and almost make my own life a big MVC in motion. I like to separate tasks the best as possible, so I can focus better. In that way, I created ````protoweb```` to focus on javascript, css/less and HTML/templates, instead all this plus request handlers, regex, console, regenerating static content and etc. And yes, I'm a Linux user, developer, sysadmin, so my head is a total mess.

## Using protoweb

As being an application, you should install it first (doh!). Grab a copy from [github](https://github.com/vltr/protoweb) or install it from pip:

````$ [sudo] pip install protoweb````

````protoweb```` should now be in your ````$PATH````. You can check if everything is working properly by simply typing:

````$ protoweb````

It should provide you the following output:

````
2013-05-29 14:53:24-0300 Log opened.
2013-05-29 14:53:24-0300 ProtoWebServer starting on 9000
2013-05-29 14:53:24-0300 Starting factory <protoweb.server.server.ProtoWebServer instance at 0x19511b8>
````

The list of options are provided by running ````protoweb```` with the ````--help```` flag:

````
$ protoweb --help
Usage: protoweb [-h]

protoweb is a simple command line tool to create rich web development
environments, with processors and the power of the Cyclone framework to handle
static and dynamic content.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SOURCE, --source=SOURCE
                        source path to run protoweb, can be more then one,
                        default: none
  -p PORT, --port=PORT  the TCP port this server will listen to, default: 9000
  -i INDEX, --index=INDEX
                        the html file in case none is found, default:
                        index.html
  -I INTERFACE, --interface=INTERFACE
                        the TCP interface you will be running, default:
                        0.0.0.0
  -L, --use-less        use the Less CSS processor for *.less files, default:
                        False
  -n, --no-templates    disable the usage of Cyclone templates: False

  Less options:
    -l LESS-FLAGS, --less-flag=LESS-FLAGS
                        less desired compilation flag, can be more then one

  Cyclone template options:
    -j JSON_PATH, --json-path=JSON_PATH
                        the JSON path in case of usage of Cyclone templates,
                        default: .

Copyright 2013 Richard Kuesters <rkuesters@gmail.com> and released under the
MIT LICENSE <http://opensource.org/licenses/MIT>. Visit us on
https://github.com/vltr/protoweb for more information.
````

Yes, protoweb needs a lot of documentation, improvements, polishing, and so on. You can check the TODO list. I'll be very pleased if anyone sends pull requests :)

## Performance

Do not expect any word for this particular item while no buffer / caching engine is embed into protoweb :)

### A note on using LESS CSS

One of my goals with ````protoweb```` was to deliver a fast LESS prototyping environment, specially testing with older browsers (the ones *we love*), where including ````less.js```` inside the ````<head>```` tag means headaches and broken layouts.

So, to have Less up and running, you **must** have Node.js installed in your system. You can find more information on how to install it from [here](http://nodejs.org/download/) or [here](https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager).

Having Node.js installed, you must install Less using npm:

````
$ [sudo] npm install less
````

Check if ````lessc```` exists and you're good to go!

````
$ which lessc
````

**PS:** it's good to check Less' compiler flags. They're accepted by ````protoweb````, but I think you would like to leave it with defaults ;)

# TODO list

- [ ] better documentation;
- [ ] better error handling, with tracebacks, colored output - if necessary;
- [ ] better logging (basically for processors);
- [ ] create a simple dynamic routing engine for Javascript development;
- [ ] REST server mocks;
- [ ] gateway proxies for HTTP[S] requests;
- [ ] provide a plugin system for processors;
- [ ] separate template engines - if users decide to use any other;
- [ ] why not use other web platforms, and not only Cyclone?
- [ ] as of Cyclone, make better use of its template engine (some functions are not working, like ````static_url```` - because I don't really have a *static* handler);
- [ ] buffering, caching, auto-reload?
- [ ] static export engine?

# Special thanks

* [Humantech Gestao do Conhecimento](https://www.humantech.com.br/), for giving me work and the opportunity to create this tool. I mean, it's your tool, AFAIK;
* My work colleagues and friends that shares the necessity of fast prototyping :)
* My [music](http://www.last.fm/user/rkues) - for preventing me from loosing more focus, lol; and
* The majestic open source community.
