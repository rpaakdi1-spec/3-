/* 
 * Dispatch Rules API Client Fix
 * Copy this code to your frontend dispatch rules API service
 */

// TypeScript/JavaScript API Client for Dispatch Rules

// ================================
// OPTION 1: Fix in API Service
// ================================

// File: src/services/api/dispatchRules.ts (or similar)

interface DispatchRuleUpdate {
  name?: string;
  description?: string;
  rule_type?: 'assignment' | 'constraint' | 'optimization';
  priority?: number;
  is_active?: boolean;
  conditions?: any;
  actions?: any;
}

interface DispatchRule {
  id: number;
  name: string;
  description: string;
  rule_type: string;
  priority: number;
  is_active: boolean;
  conditions: any;
  actions: any;
  version: number;
  created_at: string;
  updated_at: string;
}

// ❌ WRONG (Before)
export const updateDispatchRule_WRONG = async (
  id: number, 
  data: DispatchRuleUpdate
): Promise<DispatchRule> => {
  const response = await fetch(`/api/v1/dispatch-rules/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)  // ❌ Missing wrapper
  });
  return response.json();
};

// ✅ CORRECT (After)
export const updateDispatchRule = async (
  id: number, 
  data: DispatchRuleUpdate
): Promise<DispatchRule> => {
  const response = await fetch(`/api/v1/dispatch-rules/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      rule_update: data  // ✅ Wrap in rule_update
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update dispatch rule');
  }
  
  return response.json();
};

// ================================
// OPTION 2: Fix in React Component
// ================================

// React Component Example
import React, { useState } from 'react';

const DispatchRuleEdit = ({ rule, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: rule.name,
    priority: rule.priority,
    is_active: rule.is_active
  });
  
  // ❌ WRONG (Before)
  const handleSubmit_WRONG = async () => {
    const response = await fetch(`/api/v1/dispatch-rules/${rule.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)  // ❌ Missing wrapper
    });
    
    if (response.ok) {
      const updated = await response.json();
      onUpdate(updated);
    }
  };
  
  // ✅ CORRECT (After)
  const handleSubmit = async () => {
    const response = await fetch(`/api/v1/dispatch-rules/${rule.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rule_update: formData  // ✅ Wrap in rule_update
      })
    });
    
    if (response.ok) {
      const updated = await response.json();
      onUpdate(updated);
    } else {
      const error = await response.json();
      console.error('Update failed:', error);
      alert('수정 실패: ' + (error.detail || 'Unknown error'));
    }
  };
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      <input 
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
      />
      <input 
        type="number"
        value={formData.priority}
        onChange={(e) => setFormData({...formData, priority: parseInt(e.target.value)})}
      />
      <button type="submit">수정</button>
    </form>
  );
};

// ================================
// OPTION 3: Fix with Axios
// ================================

import axios from 'axios';

// ❌ WRONG (Before)
export const updateDispatchRule_Axios_WRONG = async (
  id: number,
  data: DispatchRuleUpdate
) => {
  const response = await axios.put(`/api/v1/dispatch-rules/${id}`, data);
  return response.data;
};

// ✅ CORRECT (After)
export const updateDispatchRule_Axios = async (
  id: number,
  data: DispatchRuleUpdate
) => {
  const response = await axios.put(`/api/v1/dispatch-rules/${id}`, {
    rule_update: data  // ✅ Wrap in rule_update
  });
  return response.data;
};

// ================================
// Testing Function
// ================================

export const testDispatchRuleUpdate = async (ruleId: number) => {
  try {
    console.log('Testing dispatch rule update...');
    
    const testData = {
      name: '테스트수정_' + new Date().getTime(),
      priority: 999
    };
    
    const response = await fetch(`/api/v1/dispatch-rules/${ruleId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rule_update: testData
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ Update successful:', result);
      return result;
    } else {
      const error = await response.json();
      console.error('❌ Update failed:', error);
      throw error;
    }
  } catch (err) {
    console.error('❌ Network error:', err);
    throw err;
  }
};

// ================================
// Usage Examples
// ================================

// Example 1: Update name and priority
const example1 = async () => {
  const updated = await updateDispatchRule(3, {
    name: '긴급 배차 최우선',
    priority: 200
  });
  console.log('Updated rule:', updated);
};

// Example 2: Activate/deactivate
const example2 = async () => {
  const updated = await updateDispatchRule(3, {
    is_active: false
  });
  console.log('Deactivated rule:', updated);
};

// Example 3: Full update
const example3 = async () => {
  const updated = await updateDispatchRule(3, {
    name: '수정된 규칙',
    description: '새로운 설명',
    priority: 150,
    is_active: true,
    conditions: {
      order_priority: 'urgent'
    },
    actions: {
      action_type: 'assign_nearest_vehicle',
      parameters: {
        max_distance_km: 10
      }
    }
  });
  console.log('Fully updated rule:', updated);
};

// ================================
// Browser Console Quick Test
// ================================

/*
Open http://139.150.11.99/dispatch-rules
Open Developer Tools (F12) > Console
Paste and run:

fetch('/api/v1/dispatch-rules/3', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    rule_update: {
      name: '콘솔테스트_' + Date.now(),
      priority: 888
    }
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Success:', data);
  alert('수정 성공! Version: ' + data.version);
})
.catch(err => {
  console.error('❌ Error:', err);
  alert('수정 실패!');
});
*/
