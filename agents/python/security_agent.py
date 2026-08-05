"""
Security Agent - Hybrid Implementation
Execution: Python (basic) + LLM (complex authorization)

Purpose: Generate role enums, basic authorization attributes,
and prepare prompts for complex authorization logic.
"""

import os
from typing import Dict, List, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import ParsedModule


class SecurityAgent:
    """
    Hybrid agent - Python for basic, LLM for complex authorization.
    Generates security-related code.
    """
    
    def __init__(self, target_namespace: str = "MyApp"):
        self.namespace = target_namespace
    
    def generate_all(
        self,
        modules: Dict[str, ParsedModule],
        output_dir: str
    ) -> Dict[str, str]:
        """Generate all security-related code."""
        os.makedirs(output_dir, exist_ok=True)
        
        generated = {}
        
        roles = self._collect_roles(modules)
        screens_with_roles = self._collect_screen_roles(modules)
        
        generated["Roles.cs"] = self._generate_roles_enum(roles, output_dir)
        generated["Policies.cs"] = self._generate_policies(roles, output_dir)
        generated["AuthorizationExtensions.cs"] = self._generate_auth_extensions(output_dir)
        
        if screens_with_roles:
            generated["_llm_prompt.txt"] = self._generate_llm_prompt(
                screens_with_roles, output_dir
            )
        
        return generated
    
    def _collect_roles(self, modules: Dict[str, ParsedModule]) -> List[str]:
        """Collect all roles from modules."""
        roles = set()
        for module in modules.values():
            for role in module.roles:
                roles.add(role.get("name", ""))
        
        roles.discard("")
        roles.add("Admin")
        roles.add("User")
        
        return sorted(roles)
    
    def _collect_screen_roles(
        self,
        modules: Dict[str, ParsedModule]
    ) -> List[Dict]:
        """Collect screens with role requirements."""
        screens = []
        for module in modules.values():
            for screen in module.screens:
                screens.append({
                    "module": module.module_name,
                    "screen": screen.get("name"),
                    "title": screen.get("title", "")
                })
        return screens
    
    def _generate_roles_enum(self, roles: List[str], output_dir: str) -> str:
        """Generate roles enum."""
        role_values = "\n    ".join([f'{role},' for role in roles])
        
        code = f"""namespace {self.namespace}.Security;

/// <summary>
/// Application roles migrated from OutSystems.
/// </summary>
public enum AppRoles
{{
    {role_values}
}}

/// <summary>
/// Role constants for policy names.
/// </summary>
public static class RoleNames
{{
{chr(10).join([f'    public const string {role} = "{role}";' for role in roles])}
}}
"""
        
        output_path = os.path.join(output_dir, "Roles.cs")
        with open(output_path, 'w') as f:
            f.write(code)
        
        return output_path
    
    def _generate_policies(self, roles: List[str], output_dir: str) -> str:
        """Generate authorization policies."""
        policy_configs = []
        for role in roles:
            policy_configs.append(
                f'        options.AddPolicy("{role}Policy", policy => policy.RequireRole(RoleNames.{role}));'
            )
        
        code = f"""using Microsoft.AspNetCore.Authorization;

namespace {self.namespace}.Security;

/// <summary>
/// Authorization policy configuration.
/// </summary>
public static class AuthorizationPolicies
{{
    public static void Configure(AuthorizationOptions options)
    {{
{chr(10).join(policy_configs)}
        
        // Combined policies
        options.AddPolicy("AdminOrManager", policy => 
            policy.RequireRole(RoleNames.Admin));
        
        options.AddPolicy("Authenticated", policy => 
            policy.RequireAuthenticatedUser());
    }}
}}
"""
        
        output_path = os.path.join(output_dir, "Policies.cs")
        with open(output_path, 'w') as f:
            f.write(code)
        
        return output_path
    
    def _generate_auth_extensions(self, output_dir: str) -> str:
        """Generate authorization service extensions."""
        code = f"""using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.DependencyInjection;

namespace {self.namespace}.Security;

/// <summary>
/// Authorization service registration extensions.
/// </summary>
public static class AuthorizationExtensions
{{
    public static IServiceCollection AddAppAuthorization(this IServiceCollection services)
    {{
        services.AddAuthorization(AuthorizationPolicies.Configure);
        
        return services;
    }}
}}

/// <summary>
/// Custom authorization handler for complex scenarios.
/// Extend this for resource-based authorization.
/// </summary>
public class ResourceAuthorizationHandler : AuthorizationHandler<ResourceRequirement, object>
{{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        ResourceRequirement requirement,
        object resource)
    {{
        // TODO: Implement resource-based authorization
        // This is where LLM-generated complex logic goes
        
        if (context.User.IsInRole(RoleNames.Admin))
        {{
            context.Succeed(requirement);
        }}
        
        return Task.CompletedTask;
    }}
}}

/// <summary>
/// Resource requirement for authorization.
/// </summary>
public class ResourceRequirement : IAuthorizationRequirement
{{
    public string Operation {{ get; }}
    
    public ResourceRequirement(string operation)
    {{
        Operation = operation;
    }}
}}
"""
        
        output_path = os.path.join(output_dir, "AuthorizationExtensions.cs")
        with open(output_path, 'w') as f:
            f.write(code)
        
        return output_path
    
    def _generate_llm_prompt(
        self,
        screens_with_roles: List[Dict],
        output_dir: str
    ) -> str:
        """Generate prompt for LLM to handle complex authorization."""
        screen_list = "\n".join([
            f"- {s['module']}.{s['screen']}: {s['title']}"
            for s in screens_with_roles[:50]
        ])
        
        prompt = f"""Generate complex authorization logic for the following screens migrated from OutSystems.

## Screens Requiring Authorization:
{screen_list}

## Requirements:
1. Create IAuthorizationRequirement implementations for each access pattern
2. Create AuthorizationHandler<TRequirement> for each requirement
3. Consider resource-based authorization where appropriate
4. Handle multi-tenant scenarios if applicable

## Output Format:
Generate C# code for:
1. Custom requirements (e.g., CanEditDocumentRequirement)
2. Authorization handlers
3. Policy configurations

## Target Namespace: {self.namespace}.Security

Generate the authorization code:
"""
        
        output_path = os.path.join(output_dir, "_llm_prompt.txt")
        with open(output_path, 'w') as f:
            f.write(prompt)
        
        return output_path


if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Generate security code")
    parser.add_argument("input_dir", help="Directory with parsed JSON files")
    parser.add_argument("-o", "--output", default="./Security", help="Output directory")
    parser.add_argument("-n", "--namespace", default="MyApp", help="Target namespace")
    args = parser.parse_args()
    
    modules = {}
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".json") and not filename.startswith("_"):
            filepath = os.path.join(args.input_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
                module = ParsedModule(**data)
                modules[module.module_name] = module
    
    agent = SecurityAgent(target_namespace=args.namespace)
    generated = agent.generate_all(modules, args.output)
    
    print(f"Generated {len(generated)} security files:")
    for name, path in generated.items():
        print(f"  - {name}: {path}")
