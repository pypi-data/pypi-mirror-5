#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import s3


def main():
    """ Entry point for the package, as defined in setup.py. """
    
    # Get command line input/output arguments
    parser = argparse.ArgumentParser(
        description='Instantly deploy static HTML sites to S3 at the command line.'
    )
    parser.add_argument(
        'www_dir',
        help='Directory containing the HTML files for your website.'
    )
    parser.add_argument(
        'bucket_name',
        help='Name of S3 bucket to deploy to, e.g. mybucket.'
    )
    args = parser.parse_args()
    
    # Deploy the site to S3!
    s3.deploy(args.www_dir, args.bucket_name)


if __name__ == '__main__':
    main()
