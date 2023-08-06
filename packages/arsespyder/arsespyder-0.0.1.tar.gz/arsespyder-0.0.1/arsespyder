#!/usr/bin/env python
#
# Copyright 2013-2014 Sergio Arroutbi Braojos <sarroutbi@yahoo.es>
# 
# Permission to use, copy, modify, and/or distribute this software 
# for any purpose with or without fee is hereby granted, provided that 
# the above copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, 
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, 
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH 
# THE USE OR PERFORMANCE OF THIS SOFTWARE
#
import pyarsespyder
import argparse

def main ():
    """ main() method of the arsespyder Web crawler """

    parser = argparse.ArgumentParser(description='Internet Crawler',
                                     version = '0.0.1')
    parser.add_argument('-n', '--number-of-levels',
                        type = int, default = 3, help = 'Crawling depth')
    parser.add_argument('url', nargs=1, help = 'URL to crawl')

    args = parser.parse_args()                        
    max_depth = args.number_of_levels
    url = args.url

    pyarsespyder.print_links_to_level(url[0], max_depth)

if __name__ == '__main__':
    main()
