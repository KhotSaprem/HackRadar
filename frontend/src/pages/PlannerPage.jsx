import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getHackathon, getPlannerItems, createPlannerItem, updatePlannerItem, deletePlannerItem } from '../api'
import { getSessionId } from '../lib/session'

function PlannerPage() {
  const { id } = useParams()
  const [hackathon, setHackathon] = useState(null)
  const [plannerItems, setPlannerItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const sessionId = getSessionId()

  const [formData, setFormData] = useState({
    title: '',
    start_time: '',
    end_time: '',
    description: '',
    type: 'build',
    color: '#3B82F6'
  })

  const planTypes = [
    { value: 'idea', label: 'Idea', color: '#10B981' },
    { value: 'build', label: 'Build', color: '#3B82F6' },
    { value: 'submit', label: 'Submit', color: '#F59E0B' },
    { value: 'sleep', label: 'Sleep', color: '#6B7280' },
    { value: 'review', label: 'Review', color: '#8B5CF6' },
    { value: 'meeting', label: 'Meeting', color: '#EF4444' }
  ]

  useEffect(() => {
    console.log('PlannerPage: useEffect triggered, id:', id)
    loadData()
  }, [id])

  const loadData = async () => {
    try {
      console.log('PlannerPage: Loading data for hackathon:', id, 'session:', sessionId)
      setLoading(true)
      const [hackathonData, plannerData] = await Promise.all([
        getHackathon(id),
        getPlannerItems(id, sessionId)
      ])
      console.log('PlannerPage: Loaded hackathon:', hackathonData)
      console.log('PlannerPage: Loaded planner items:', plannerData)
      setHackathon(hackathonData)
      setPlannerItems(plannerData)
    } catch (err) {
      console.error('PlannerPage: Error loading data:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const itemData = {
        ...formData,
        hackathon_id: id,
        session_id: sessionId,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString()
      }

      if (editingItem) {
        await updatePlannerItem(editingItem.id, itemData)
      } else {
        await createPlannerItem(itemData)
      }

      await loadData()
      resetForm()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEdit = (item) => {
    setEditingItem(item)
    setFormData({
      title: item.title,
      start_time: new Date(item.start_time).toISOString().slice(0, 16),
      end_time: new Date(item.end_time).toISOString().slice(0, 16),
      description: item.description || '',
      type: item.type || 'build',
      color: item.color || '#3B82F6'
    })
    setShowAddForm(true)
  }

  const handleDelete = async (itemId) => {
    if (window.confirm('Are you sure you want to delete this plan item?')) {
      try {
        await deletePlannerItem(itemId)
        await loadData()
      } catch (err) {
        setError(err.message)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      start_time: '',
      end_time: '',
      description: '',
      type: 'build',
      color: '#3B82F6'
    })
    setEditingItem(null)
    setShowAddForm(false)
  }

  const exportCalendar = () => {
    const url = `/api/planner/${id}/export/ics?session_id=${sessionId}`
    window.open(url, '_blank')
  }

  console.log('PlannerPage: Render - loading:', loading, 'error:', error, 'hackathon:', hackathon, 'sessionId:', sessionId)

  if (loading) return <div className="loading" style={{padding: '2rem', textAlign: 'center'}}>Loading planner...</div>
  if (error) return <div className="error" style={{padding: '2rem', textAlign: 'center', color: 'red'}}>Error: {error}</div>
  if (!hackathon) return <div className="error" style={{padding: '2rem', textAlign: 'center', color: 'red'}}>Hackathon not found</div>

  return (
    <div className="planner-page" style={{minHeight: '100vh', background: '#f8fafc'}}>
      <div style={{padding: '1rem', background: 'yellow', color: 'black'}}>
        DEBUG: Planner page loaded for hackathon: {hackathon?.title} (ID: {id})
      </div>
      <div className="container" style={{maxWidth: '1200px', margin: '0 auto', padding: '0 1rem'}}>
        <div className="planner-header">
          <Link to={`/hackathon/${id}`} className="back-link">← Back to Hackathon</Link>
          <h1>Planner: {hackathon.title}</h1>
          <div className="planner-actions">
            <button onClick={() => setShowAddForm(true)} className="btn btn-primary">
              Add Plan Item
            </button>
            {plannerItems.length > 0 && (
              <button onClick={exportCalendar} className="btn btn-secondary">
                Export Calendar
              </button>
            )}
          </div>
        </div>

        {showAddForm && (
          <div className="add-form-overlay">
            <div className="add-form">
              <h3>{editingItem ? 'Edit Plan Item' : 'Add Plan Item'}</h3>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Title</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    required
                  />
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Start Time</label>
                    <input
                      type="datetime-local"
                      value={formData.start_time}
                      onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>End Time</label>
                    <input
                      type="datetime-local"
                      value={formData.end_time}
                      onChange={(e) => setFormData({...formData, end_time: e.target.value})}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Type</label>
                    <select
                      value={formData.type}
                      onChange={(e) => {
                        const selectedType = planTypes.find(t => t.value === e.target.value)
                        setFormData({
                          ...formData, 
                          type: e.target.value,
                          color: selectedType?.color || '#3B82F6'
                        })
                      }}
                    >
                      {planTypes.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Color</label>
                    <input
                      type="color"
                      value={formData.color}
                      onChange={(e) => setFormData({...formData, color: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows="3"
                  />
                </div>

                <div className="form-actions">
                  <button type="submit" className="btn btn-primary">
                    {editingItem ? 'Update' : 'Add'} Item
                  </button>
                  <button type="button" onClick={resetForm} className="btn btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="planner-timeline">
          {plannerItems.length === 0 ? (
            <div className="empty-state">
              <p>No plan items yet. Add your first item to get started!</p>
            </div>
          ) : (
            <div className="timeline">
              {plannerItems.map(item => (
                <div key={item.id} className="timeline-item" style={{borderLeftColor: item.color}}>
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <h4>{item.title}</h4>
                      <div className="timeline-actions">
                        <button onClick={() => handleEdit(item)} className="btn-icon">✏️</button>
                        <button onClick={() => handleDelete(item.id)} className="btn-icon">🗑️</button>
                      </div>
                    </div>
                    <div className="timeline-meta">
                      <span className="time">
                        {new Date(item.start_time).toLocaleString()} - {new Date(item.end_time).toLocaleString()}
                      </span>
                      <span className="type" style={{backgroundColor: item.color}}>
                        {planTypes.find(t => t.value === item.type)?.label || item.type}
                      </span>
                    </div>
                    {item.description && (
                      <p className="timeline-description">{item.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PlannerPage