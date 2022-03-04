#!/usr/bin/python

import os, sys
from os.path import exists
import argparse
import time
import glob
import subprocess
import mock
import unittest
import shlex
import json

scriptlocation = os.path.dirname(__file__)
helm_chart_location = os.path.join(scriptlocation, "..", "k8s")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def system_no_out(command, checkReturnValue=True):
    ret = subprocess.call(shlex.split(command),stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if checkReturnValue and ret != 0:
        eprint("Command failed: {}".format(command))
        sys.exit(1)
    return ret

def capture_std_out_of_command(command):
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    capture = ""

    s = process.stdout.read(1)
    while len(s) > 0:
        sys.stdout.write(s)
        sys.stdout.flush()
        capture += s
        s = process.stdout.read(1)

    return capture

def get_column_of_list_command(command, column_number):
    std_out = capture_std_out_of_command(command)
    result = []
    for line in std_out.splitlines()[1:]:
        cells = line.split()
        result.append(cells[column_number])
    return result

def system(command, checkReturnValue=True):
    ret = os.system(command)
    if checkReturnValue and ret != 0:
        eprint("Command failed: {}".format(command))
        sys.exit(1)
    return ret

def system_retry(command, max_retries=10, sleep_time=5):
    retries = 0
    while True:
        ret = system(command, checkReturnValue=False)
        if ret == 0:
            return ret
        retries += 1
        eprint("Retrying")
        if retries > max_retries:
            eprint("Command failed: {}".format(command))
            sys.exit(1)
        time.sleep(sleep_time)

def parse_args():
    parser = argparse.ArgumentParser(description ='Installs the cockatoo backend.\nRun tests with: python -m unittest cinstall.py')
    parser.add_argument('charts', nargs='+', help='The helm charts to be installed')
    parser.add_argument('--reinstall', dest ='reinstall',
                        action ='store_true', help ='Reinstalls the helm chart')
    parser.add_argument('--functionRecreate', dest ='functionRecreate',
                        action ='store_true', help ='Recreates existing Fission function resources')
    parser.add_argument('--triggerRecreate', dest ='triggerRecreate',
                        action ='store_true', help ='Recreates existing Fission trigger resources')
    parser.add_argument('--delete', dest ='delete',
                        action ='store_true', help ='Deletes the helm chart')                    
    parser.add_argument('--hardReinstall', dest ='hardReinstall',
                        action ='store_true', help ='Destroys and recreates minikube')
    parser.add_argument('--updateDependencies', dest ='updateDependencies',
                        action ='store_true', help ='Updates the helm dependencies')
    parser.add_argument('--dry-run', dest ='dryRun',
                        action ='store_true', help ='Only prints the commands that would be run')
    parser.add_argument('--prod', dest ='prod',
                        action ='store_true', help ='Targets the production system. With this command a file prod-env.json needs to be present in the same directory as this script.')
    parser.add_argument('--no-confirmation', dest ='noConfirmation',
                        action ='store_true', help ='Targets the production system without asking for confirmation. This is intended for automated installs only.')
    parser.add_argument('--use-env-vars', dest ='useEnvVars',
                        action ='store_true', help ='Takes all settings from env vars instead of loading prod-env.json. For each entry an env var prefixed with "cinstall." needs to exist')
    return parser.parse_args()

class CommandBuilder:
    def __init__(self, env, env_settings, args):
        self.commands = []
        self.checks = []
        self.env = env
        self.vars = env_settings
        self.args = args

    def check(self, check):
        self.checks.append(check)

    def system(self, command):
        self.commands.append(command)
    
    def minikube(self, arguments):
        self.system("minikube " + arguments)
    
    def helm_repo(self, arguments):
        self.system("helm repo " + arguments)

    def helm_install(self, arguments):
        self.system("helm upgrade --install " + arguments)

    def helm_delete(self, arguments):
        self.system("helm delete " + arguments)

    def kubectl(self, arguments):
        self.system("kubectl " + arguments)

    def fission(self, arguments):
        self.system("fission " + arguments)

def minikube_start(reinstall, builder):
    if builder.env == "prod":
        return

    if reinstall:
        builder.minikube("delete")
        builder.minikube("start")
        builder.minikube("addons enable ingress")
    else:
        minikube_status = system_no_out("minikube status", checkReturnValue=False)
        if minikube_status != 0:
            builder.minikube("start")
            builder.minikube("addons enable ingress")

class IngressChart:
    def applies_to_env(self, env):
        return env == "prod"
    def is_local_chart(self):
        return False
    def name(self):
        return "ingress"
    def delete(self, builder):
        builder.helm_delete("-n nginx ingress-controller")
    def install(self, builder):
        builder.helm_repo("add ingress-nginx https://kubernetes.github.io/ingress-nginx")
        builder.helm_repo("update")
        builder.helm_install("ingress-controller ingress-nginx/ingress-nginx --create-namespace -n nginx")

class CertChart:
    def applies_to_env(self, env):
        return env == "prod"
    def is_local_chart(self):
        return False
    def name(self):
        return "cert"
    def delete(self, builder):
        builder.helm_delete("-n cert-manager cert")
    def install(self, builder):
        builder.helm_repo("add jetstack https://charts.jetstack.io")
        builder.helm_repo("update")
        builder.helm_install("--create-namespace -n cert-manager cert jetstack/cert-manager --set installCRDs=true --version v1.7.1")
        cert = os.path.join(helm_chart_location, "operators", "letsencrypt-production.yaml")
        builder.kubectl("apply -f " + cert)

class DatabaseProdChart:
    def applies_to_env(self, env):
        return env == "prod"
    def is_local_chart(self):
        return False
    def name(self):
        return "database"
    def delete(self, builder):
        builder.helm_delete("-n db database")
    def install(self, builder):
        def check_license_exists():
            if (not exists("license.txt")):
                eprint("Kube DB license file not found. Please create a Kube DB license.txt file in the current directory. Refer also to: https://kubedb.com/docs/v2021.09.30/setup/install/enterprise/")
                return False
            return True

        builder.check(check_license_exists)
        builder.helm_install("kubedb appscode/kubedb --version v2021.12.21 --namespace kubedb --create-namespace --set kubedb-enterprise.enabled=true --set kubedb-autoscaler.enabled=true --set-file global.license=license.txt")
        builder.helm_install("stash appscode/stash --version v2022.02.22 --namespace kubedb --create-namespace --set features.enterprise=true --set-file global.license=license.txt")
        builder.kubectl("create ns db")
        builder.kubectl("create -f " + os.path.join("operators", "kubedb", "postgres.yaml"))

class DatabaseProdBackupChart:     
    def applies_to_env(self, env):
        return env == "prod"
    def is_local_chart(self):
        return True
    def name(self):
        return "dbbackup"
    def delete(self, builder):
        builder.helm_delete("-n db dbbackup")
    def install(self, builder):
        encryption_key = builder.vars["db.backup.encryptionkey"]
        access_key = builder.vars["db.backup.s3.accesskey"]
        secret = builder.vars["db.backup.s3.secret"]
        builder.helm_install(f"--create-namespace -n db dbbackup ./dbbackup --set encryptionKey={encryption_key} --set s3.accessKey={access_key} --set s3.secret={secret}")
class DatabaseDevChart:
    def applies_to_env(self, env):
        return env == "dev"
    def is_local_chart(self):
        return True
    def name(self):
        return "database"
    def delete(self, builder):
        builder.helm_delete("-n db database")
    def install(self, builder):
        builder.helm_install("--create-namespace -n db database ./database")

class MonitoringChart:
    def applies_to_env(self, _):
        return True
    def is_local_chart(self):
        return True
    def name(self):
        return "monitoring"
    def delete(self, builder):
        builder.helm_delete("-n monitoring monitoring")
    def install(self, builder):
        host = ""
        if builder.env == "prod":
            host = "--set host=" + builder.vars["apidomain"]
        builder.helm_install("--create-namespace -n monitoring monitoring ./monitoring " + host)

class AuthChart:
    def applies_to_env(self, _):
        return True
    def is_local_chart(self):
        return True
    def name(self):
        return "auth"
    def delete(self, builder):
        builder.helm_delete("-n auth auth")
    def install(self, builder):
        db_host = builder.vars["dbhost"]
        db_pw = builder.vars["authpassword"]
        database = builder.vars["dbname"]
        host = ""
        if builder.env == "prod":
            host = "--set host=" + builder.vars["authdomain"]
        builder.helm_install(f"--create-namespace -n auth auth ./auth --set db.host={db_host} --set db.user=keycloak --set db.password={db_pw} --set db.database={database} " + host)

class RavenChart:
    def applies_to_env(self, _):
        return True
    def is_local_chart(self):
        return True
    def name(self):
        return "raven"
    def delete(self, builder):
        builder.helm_delete("raven")
    def install(self, builder):
        db_host = builder.vars["dbhost"]
        db_pw = builder.vars["ravenpassword"]
        api_key = builder.vars["apikey"]
        db_name = "postgres" if builder.env == "prod" else "cockatoo"
        builder.helm_install(f"raven ./raven --set db.host={db_host} --set db.name={db_name} --set db.user=raven --set db.password={db_pw} --set db.url=jdbc:postgresql://{db_host}:5432/{db_name} --set auth.url=http://auth-keycloak-http.auth.svc.cluster.local --set api_key={api_key}")

class FissionFunctions:
    def applies_to_env(self, _):
        return True
    def is_local_chart(self):
        return False
    def name(self):
        return "functions"
    def delete(self, builder):
        builder.fission("spec destroy")
        eprint("Recreating fission specs")
        for file in glob.glob("specs/function*.yaml"):    
            os.remove(file)
        for file in glob.glob("specs/route*.yaml"):    
            os.remove(file)
    def install(self, builder):
        builder.fission("spec apply")
        existing_functions = get_column_of_list_command("fission function list", 0)
        existing_triggers = get_column_of_list_command("fission httptrigger list", 0)
        for file in glob.glob("dist/*.js"):
            file_name = os.path.basename(file).replace(".js", "") # E.g. /home/me/v1-journal.ts => crud-v1-journal
            operations = file_name.split("-")[0] # E.g. crud-v1-journal => crud
            function_name_parts = file_name.split("-")[1:]
            function_name = str.join("", function_name_parts) # E.g. crud-v1-journal => v1-journal
            route = "/" + str.join("/", function_name_parts) # E.g. v1-journal => /v1/journal
            http_operations = []
            for char in operations:
                if char == "r":
                    http_operations.append("GET")
                elif char == "u":
                    http_operations.append("PATCH")
                elif char == "c":
                    http_operations.append("POST")
                    http_operations.append("PUT")
                elif char == "d":
                    http_operations.append("DELETE")
            all_operations = str.join(" ", ["--method " + m for m in http_operations])

            is_existing_function = function_name in existing_functions
            if not is_existing_function or args.functionRecreate:
                function_action = "update" if is_existing_function else "create"
                builder.fission(f"function {function_action} --name {function_name} --env nodejs --code {file} --secret ravensecrets")
            if is_existing_function:
                existing_functions.remove(function_name)

            is_existing_trigger = function_name in existing_triggers
            if not is_existing_trigger or args.triggerRecreate:
                host = builder.vars["apidomain"]
                domain = f"--ingressrule \"{host}={route}\" --ingressannotation \"cert-manager.io/cluster-issuer=letsencrypt-production\" --ingressannotation \"kubernetes.io/ingress.class=nginx\" --ingresstls letsencrypt-production " if builder.env == "prod" else ""
                route_action = "update" if is_existing_trigger else "create"
                builder.fission(f"httptrigger {route_action} --name {function_name} --url {route} {domain} --function {function_name} --createingress --method OPTIONS {all_operations}") 
            if is_existing_trigger:
                existing_triggers.remove(function_name)                
        for obsolete_function in existing_functions:
            builder.fission(f"function delete --name {obsolete_function}")
        for obsolete_trigger in existing_triggers:
            builder.fission(f"httptrigger delete --name {obsolete_trigger}")


def get_charts_install_order():
    return [IngressChart(), DatabaseDevChart(), DatabaseProdChart(), DatabaseProdBackupChart(), CertChart(), MonitoringChart(), AuthChart(), RavenChart(), FissionFunctions()]

def get_env(args):
    if args.prod == True:
        eprint("Targeting production system")
        return "prod"
    else:
        return "dev"

def get_charts(env, chartnames):
    chart_install_order = get_charts_install_order()

    if "full" in chartnames:
        return [chart for chart in chart_install_order if chart.applies_to_env(env)]
    else:
        charts = []
        for chart in chartnames:
            if not any(c.name() == chart for c in chart_install_order):
                eprint("{} is not a valid chart".format(chart))
        # Adding charts this way removes duplicates and preserves order
        for chart in chart_install_order:
            if chart.name() in chartnames:
                if chart.applies_to_env(env):
                    charts.append(chart)
        return charts

def check(builder):
    ok = True
    for check in builder.checks:
        ok = ok and check()
    return ok

def install_charts(builder, charts):
    for chart in charts:
        chart.install(builder)

def delete_charts(builder, charts):
    for chart in charts:
        chart.delete(builder)

def update_helm_dependencies():
    chart_install_order = get_charts_install_order()
    for chart in chart_install_order:
        if chart.is_local_chart():
            os.chdir(chart.name())
            system("helm dependency update")
            os.chdir("..")

def load_env_file(env, useEnvVars):
    if env == "prod" == True and useEnvVars == True:
        template = load_env_file("dev", False)
        for key in template.keys():
            template[key] = os.environ["cinstall." + key]
        return template
        
    with open(env + "-env.json") as f:
        lines = f.readlines()
        return json.loads(str.join("\n", lines))


def main(args):
    env = get_env(args)
    env_settings = load_env_file(env, args.useEnvVars)
    commands = CommandBuilder(env, env_settings, args)
    if args.updateDependencies:
        update_helm_dependencies()
    minikube_start(args.hardReinstall, commands)
    charts = get_charts(env, args.charts)
    if args.delete:
        delete_charts(commands, charts)
    else:
        install_charts(commands, charts)
        
    if not check(commands):
        eprint("One or more checks failed. Aborting.")
        sys.exit(1)

    eprint("Going to execute:")
    for command in commands.commands:
        eprint("# " + command)

    if args.dryRun:
        return      
    if args.prod and not args.noConfirmation:
        eprint("This is a production system. Are you sure you want to do this? (yes/no)")
        answer = input()
        if answer != "yes":
            eprint("Aborting")
            sys.exit(1)

    for command in commands.commands:
        eprint("Executing: " + command)
        system(command)

class TestSum(unittest.TestCase):

    def get_command_builder(self, env):
        env_settings = {
            "apidomain": "test.app",
            "authdomain": "test.app",
            "dbhost": "test-database",
            "authpassword": "keyclo@k",
            "ravenpassword": "r@aven",
            "db.backup.encryptionkey": "",
            "db.backup.s3.accesskey": "",
            "db.backup.s3.secret": "",
        }
        return CommandBuilder(env, env_settings, None)

    def get_chart_names(self, env, chartnames):
        return [chart.name() for chart in get_charts(env, chartnames)]

    def test_get_env(self):
        args = mock.Mock()
        self.assertEqual(get_env(args), "dev")
        args.prod = True
        self.assertEqual(get_env(args), "prod")

    def test_valid_charts(self):
        self.assertEqual(self.get_chart_names("prod",  ["ingress", "monitoring"]), ["ingress", "monitoring"])

    def test_invalid_charts(self):
        self.assertEqual(self.get_chart_names("prod", ["ingress", "notthere"]), ["ingress"])

    def test_filter_full_for_prod(self):
        self.assertEqual(self.get_chart_names("prod", ["full"]), ["ingress", "database", "dbbackup", "cert", "monitoring", "auth", "raven", "functions"])

    def test_filter_full_for_dev(self):
        self.assertEqual(self.get_chart_names("dev", ["full"]), ["database", "monitoring", "auth", "raven", "functions"])

    def test_filter_for_prod(self):
        self.assertEqual(self.get_chart_names("prod", ["ingress", "cert", "database", "monitoring"]), ["ingress", "database", "cert", "monitoring"])

    def test_filter_for_dev(self):
        self.assertEqual(self.get_chart_names("dev", ["ingress", "cert", "database", "monitoring"]), ["database", "monitoring"])

    def test_minikube_start_does_nothing_on_prod(self):
        commands = self.get_command_builder("prod")
        minikube_start(False, commands)
        self.assertEqual(commands.commands, [])
        minikube_start(True, commands)
        self.assertEqual(commands.commands, [])

    def test_minikube_start_on_dev(self):
        commands = self.get_command_builder("dev")
        minikube_start(True,  commands)
        self.assertEqual(commands.commands, ["minikube delete", "minikube start", "minikube addons enable ingress"])


if __name__=="__main__":
    args = parse_args()
    cwd = os.getcwd()
    try:
        os.chdir(helm_chart_location)
        main(args)
    finally:
        os.chdir(cwd)