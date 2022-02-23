#!/usr/bin/bash

kubectl -n db port-forward svc/pgadmin 8080:80