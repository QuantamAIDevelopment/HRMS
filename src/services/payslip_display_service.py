from typing import Dict, List, Any
from decimal import Decimal

class PayslipDisplayService:
    
    @staticmethod
    def display_payslip_breakdown(payroll_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display complete payslip breakdown including core components and updated components
        """
        # Handle different data structures
        if "payslip_details" in payroll_data:
            # New structure with payslip_details
            emp_info = payroll_data.get("employee_info", {})
            payslip = payroll_data.get("payslip_details", {})
            salary_components = payslip.get("salary_components", {})
            
            employee_id = emp_info.get("employee_id")
            month = payslip.get("month", "").title()
            payroll_id = payslip.get("payroll_id", "N/A")
            
            basic_salary = float(payslip.get("basic_salary", 0))
            hra = float(payslip.get("hra", 0))
            allowance = float(payslip.get("allowance", 0))
            provident_fund_pct = float(payslip.get("provident_fund_percentage", 12))
            professional_tax = float(payslip.get("professional_tax", 200))
            provident_fund = round(basic_salary * provident_fund_pct / 100, 2)
            
            earnings_breakdown = {
                "Basic Salary": basic_salary,
                "HRA": hra,
                "Allowance": allowance
            }
            
            for component in salary_components.get("earnings", []):
                earnings_breakdown[component["component_name"]] = component["amount"]
            
            deductions_breakdown = {
                "Provident Fund": provident_fund,
                "Professional Tax": professional_tax
            }
            
            for component in salary_components.get("deductions", []):
                deductions_breakdown[component["component_name"]] = component["amount"]
            
            total_earnings = payslip.get("total_earnings", sum(earnings_breakdown.values()))
            total_deductions = payslip.get("total_deductions", sum(deductions_breakdown.values()))
            net_salary = payslip.get("net_salary", total_earnings - total_deductions)
            
        elif "salary_structure" in payroll_data:
            # Structure with salary_structure
            emp_info = payroll_data.get("employee_info", {})
            salary_struct = payroll_data.get("salary_structure", {})
            
            employee_id = emp_info.get("employee_id")
            month = salary_struct.get("month", "").title()
            payroll_id = salary_struct.get("payroll_id", "N/A")
            
            basic_salary = float(salary_struct.get("basic_salary", 0))
            hra = float(salary_struct.get("hra", 0))
            allowance = float(salary_struct.get("allowance", 0))
            provident_fund_pct = float(salary_struct.get("provident_fund_percentage", 12))
            professional_tax = float(salary_struct.get("professional_tax", 200))
            provident_fund = round(basic_salary * provident_fund_pct / 100, 2)
            
            earnings_breakdown = {
                "Basic Salary": basic_salary,
                "HRA": hra,
                "Allowance": allowance
            }
            
            deductions_breakdown = {
                "Provident Fund": provident_fund,
                "Professional Tax": professional_tax
            }
            
            total_earnings = salary_struct.get("total_earnings", sum(earnings_breakdown.values()))
            total_deductions = salary_struct.get("total_deductions", sum(deductions_breakdown.values()))
            net_salary = salary_struct.get("net_salary", total_earnings - total_deductions)
        else:
            # Old structure with updated components
            employee_id = payroll_data.get("employee_id")
            month = payroll_data.get("month", "").title()
            payroll_id = payroll_data.get("payroll_id", "N/A")
            new_totals = payroll_data.get("new_totals", {})
            updated_components = payroll_data.get("updated_components", {})
            
            total_earnings = new_totals.get("total_earnings", 0)
            basic_salary = round(total_earnings * 0.50, 2)
            hra = round(basic_salary * 0.40, 2)
            allowance = round(total_earnings * 0.15, 2)
            provident_fund = round(basic_salary * 0.12, 2)
            professional_tax = 200.00
            
            earnings_breakdown = {
                "Basic Salary": basic_salary,
                "HRA": hra,
                "Base Allowances": allowance
            }
            
            for component in updated_components.get("earnings", []):
                earnings_breakdown[component["component_name"]] = component["amount"]
            
            deductions_breakdown = {
                "Provident Fund": provident_fund,
                "Professional Tax": professional_tax
            }
            
            for component in updated_components.get("deductions", []):
                deductions_breakdown[component["component_name"]] = component["amount"]
            
            total_earnings = sum(earnings_breakdown.values())
            total_deductions = sum(deductions_breakdown.values())
            net_salary = total_earnings - total_deductions
        
        return {
            "payroll_id": payroll_id,
            "payslip_details": {
                "employee_id": employee_id,
                "month": month,
                "payroll_id": payroll_id
            },
            "earnings": earnings_breakdown,
            "deductions": deductions_breakdown,
            "summary": {
                "total_earnings": round(total_earnings, 2),
                "total_deductions": round(total_deductions, 2),
                "net_salary": round(net_salary, 2)
            }
        }
    
    @staticmethod
    def format_payslip_display(breakdown: Dict[str, Any]) -> str:
        """
        Format payslip breakdown for display
        """
        details = breakdown["payslip_details"]
        earnings = breakdown["earnings"]
        deductions = breakdown["deductions"]
        summary = breakdown["summary"]
        
        output = f"""
================================================================
                        PAYSLIP BREAKDOWN                     
================================================================
 Employee ID: {details['employee_id']:<15} Month: {details['month']:<15} 
 Payroll ID:  {details['payroll_id']:<45} 
================================================================
                         EARNINGS                             
================================================================"""
        
        for component, amount in earnings.items():
            output += f"\n {component:<35} Rs.{amount:>15,.2f} "
        
        output += f"""
================================================================
                        DEDUCTIONS                            
================================================================"""
        
        for component, amount in deductions.items():
            output += f"\n {component:<35} Rs.{amount:>15,.2f} "
        
        output += f"""
================================================================
                         SUMMARY                              
================================================================
 Total Earnings                    Rs.{summary['total_earnings']:>15,.2f} 
 Total Deductions                  Rs.{summary['total_deductions']:>15,.2f} 
 Net Salary                        Rs.{summary['net_salary']:>15,.2f} 
================================================================
        """
        
        return output

# Usage example with your provided data
if __name__ == "__main__":
    payroll_data = {
        "employee_info": {
            "employee_id": "EMP001",
            "name": "Ravi Kumar",
            "email": "ravi.kumar@example.com",
            "designation": "Software Engineer",
            "department_id": 2,
            "joining_date": "2025-08-01",
            "annual_ctc": 650000
        },
        "payslip_details": {
            "month": "march",
            "pay_cycle": "Monthly",
            "organization_name": "QAID SOFTWARE",
            "basic_salary": 21666.67,
            "hra": 10833.33,
            "allowance": 8125,
            "provident_fund_percentage": 12,
            "professional_tax": 200,
            "total_earnings": 44150,
            "total_deductions": 10666.67,
            "net_salary": 33483.33,
            "salary_components": {
                "earnings": [
                    {
                        "component_name": "Transport Allowance",
                        "amount": 1900,
                        "component_type": "Fixed"
                    },
                    {
                        "component_name": "Performance Bonus",
                        "amount": 1625,
                        "component_type": "Percentage",
                        "original_percentage": 3
                    }
                ],
                "deductions": [
                    {
                        "component_name": "Income Tax",
                        "amount": 2166.67,
                        "component_type": "Percentage",
                        "original_percentage": 4
                    }
                ]
            }
        },
        "generated_at": "2025-12-06T13:59:04.822398"
    }
    
    service = PayslipDisplayService()
    breakdown = service.display_payslip_breakdown(payroll_data)
    print(f"\nPayroll ID: {breakdown['payroll_id']}\n")
    formatted_output = service.format_payslip_display(breakdown)
    print(formatted_output)
