#:sdk Aspire.AppHost.Sdk@13.0.0-preview.1.25517.6
#:package Aspire.Hosting.NodeJs@13.0.0-preview.1.25517.6
#:package Aspire.Hosting.Python@13.0.0-preview.1.25517.6
#:package CommunityToolkit.Aspire.Hosting.NodeJS.Extensions@9.8.0

var builder = DistributedApplication.CreateBuilder(args);
#pragma warning disable ASPIREHOSTINGPYTHON001

var apiService = builder.AddPythonModule("api", "./app/api/", "uvicorn")
    .WithArgs("github_shop_api.app:app", "--reload")
    .WithUvEnvironment()
    .WithHttpEndpoint(env: "UVICORN_PORT")
    .WithExternalHttpEndpoints();
    
builder.AddViteApp("frontend", "./frontend")
    .WithNpmPackageInstallation()
    .WithReference(apiService)
    .WaitFor(apiService);

builder.Build().Run();
