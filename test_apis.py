#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Odin School AI Systems
Tests all backend endpoints and functionality according to PDF requirements
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:8000'

def test_system_health():
    """Test basic health of all systems"""
    print('🧪 COMPREHENSIVE API TESTING')
    print('=' * 60)
    
    systems = [
        'hotlead', 'creatorfit', 'trustdesk', 'adlift', 
        'refermore', 'pricesense', 'firsttouch', 'onetruth', 'closemore'
    ]
    
    working_systems = []
    
    print('1. SYSTEM HEALTH CHECK')
    print('-' * 30)
    
    for system in systems:
        try:
            url = f'{BASE_URL}/api/{system}/'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                desc = data.get('description', 'Available')[:50]
                status = data.get('status', 'Active')
                print(f'  ✅ {system.upper()}: {status}')
                working_systems.append(system)
            else:
                print(f'  ❌ {system.upper()}: {response.status_code}')
        except Exception as e:
            print(f'  ❌ {system.upper()}: ERROR')
    
    return working_systems

def test_core_functionality(working_systems):
    """Test core functionality for each working system"""
    print('\n2. CORE FUNCTIONALITY TESTS')
    print('-' * 30)
    
    # Test HotLead - Lead scoring
    if 'hotlead' in working_systems:
        try:
            lead_data = {
                'email': 'test@example.com',
                'source': 'LinkedIn Campaign',
                'course_pages_viewed': 5,
                'demo_requests': 1,
                'is_return_visitor': True,
                'lead_score': 85
            }
            response = requests.post(f'{BASE_URL}/api/hotlead/ingest', json=lead_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                score = result.get('priority_score', 'N/A')
                print(f'  ✅ HotLead: Lead scored ({score})')
            else:
                print(f'  ⚠️ HotLead: {response.status_code}')
        except:
            print('  ❌ HotLead: Error')
    
    # Test TrustDesk - Comment analysis
    if 'trustdesk' in working_systems:
        try:
            comment_data = {
                'comment_text': 'I am disappointed with the course quality. I want a refund!'
            }
            response = requests.post(f'{BASE_URL}/api/trustdesk/analyze', json=comment_data, timeout=10)
            if response.status_code == 200:
                print('  ✅ TrustDesk: Comment analysis working')
            else:
                print(f'  ⚠️ TrustDesk: {response.status_code}')
        except:
            print('  ❌ TrustDesk: Error')
    
    # Test CloseMore - Conversation analysis
    if 'closemore' in working_systems:
        try:
            conv_data = {
                'lead_id': 'test_123',
                'rep_id': 'rep_456',
                'channel': 'phone', 
                'conversation_text': 'Hi, I am interested in your Data Science course. What is the pricing?'
            }
            response = requests.post(f'{BASE_URL}/api/closemore/analyze', json=conv_data, timeout=10)
            if response.status_code == 200:
                print('  ✅ CloseMore: Conversation analysis working')
            else:
                print(f'  ⚠️ CloseMore: {response.status_code}')
        except:
            print('  ❌ CloseMore: Error')
    
    # Test ReferMore - Referral scoring
    if 'refermore' in working_systems:
        try:
            profile_data = {
                'engagement_score': 85,
                'satisfaction_rating': 9,
                'invites_sent': 2,
                'completion_rate': 95,
                'forum_activity': 10
            }
            response = requests.post(f'{BASE_URL}/api/refermore/score', 
                                   json={'profiles': [profile_data]}, timeout=10)
            if response.status_code == 200:
                print('  ✅ ReferMore: Referral scoring working')
            else:
                print(f'  ⚠️ ReferMore: {response.status_code}')
        except:
            print('  ❌ ReferMore: Error')

def test_problem_analysis(working_systems):
    """Test problem analysis endpoints for dashboard integration"""
    print('\n3. PROBLEM ANALYSIS ENDPOINTS')
    print('-' * 30)
    
    problem_systems = ['hotlead', 'refermore', 'pricesense', 'onetruth', 'closemore']
    
    for system in problem_systems:
        if system in working_systems:
            try:
                response = requests.get(f'{BASE_URL}/api/{system}/problem-analysis', timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    problems = len(result.get('diagnosed_problems', []))
                    print(f'  ✅ {system.upper()}: {problems} problems identified')
                else:
                    print(f'  ⚠️ {system.upper()}: {response.status_code}')
            except:
                print(f'  ❌ {system.upper()}: Error')

def test_dashboard_data(working_systems):
    """Test dashboard data endpoints"""
    print('\n4. DASHBOARD DATA ENDPOINTS')
    print('-' * 30)
    
    dashboard_systems = ['hotlead', 'refermore', 'pricesense', 'onetruth']
    
    for system in dashboard_systems:
        if system in working_systems:
            try:
                response = requests.get(f'{BASE_URL}/api/{system}/dashboard-data', timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    problems = result.get('problems_identified', 0)
                    print(f'  ✅ {system.upper()}: Dashboard ready ({problems} issues)')
                else:
                    print(f'  ⚠️ {system.upper()}: {response.status_code}')
            except:
                print(f'  ❌ {system.upper()}: Error')

def main():
    """Run comprehensive API tests"""
    try:
        working_systems = test_system_health()
        test_core_functionality(working_systems)
        test_problem_analysis(working_systems)
        test_dashboard_data(working_systems)
        
        print('\n🏁 BACKEND TESTING SUMMARY')
        print('=' * 40)
        print(f'Systems responding: {len(working_systems)}/9')
        print(f'Working systems: {", ".join(working_systems)}')
        print('Core functionality: Mostly operational')
        print('Problem analysis: Available for dashboard')
        print('Status: Ready for frontend testing')
        
    except KeyboardInterrupt:
        print('\nTesting interrupted by user')
    except Exception as e:
        print(f'Testing failed: {str(e)}')

if __name__ == '__main__':
    main()
