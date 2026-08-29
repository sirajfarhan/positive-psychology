import { useEffect, useState } from 'react'
import { Compass } from '@phosphor-icons/react'

const SCALE = 3 // raw 1-7 with neutral at 4, so oriented runs -3..+3

/** As a share of the way to the pole. 100% is the far end of the rail. */
const pctOf = (v) => Math.round((Math.min(Math.abs(v), SCALE) / SCALE) * 100)

/** One bar growing from the centre spine, left or right. */
function Row({ row, overall = false }) {
  const { left, right, value, n } = row
  const pct = pctOf(value) / 2 // half-width, since the bar starts at centre
  const good = value >= 0
  const zero = pctOf(value) === 0
  const colour = zero ? 'var(--dim)' : good ? 'var(--good)' : 'var(--bad)'
  // past this the label would collide with the pole word, so it sits inside
  const inside = pctOf(value) > 84
  const sign = zero ? '' : good ? '+' : '−'

  return (
    <div className={`row${row.aside ? ' aside' : ''}`}>
      <div className="pole left">{left}</div>

      <div className="track">
        <div className="rail" />
        <div className="spine" />
        <div
          className="bar"
          style={{
            background: colour,
            width: `${pct}%`,
            left: good ? '50%' : `${50 - pct}%`,
          }}
          title={`${value > 0 ? '+' : ''}${value.toFixed(2)} of 3 · from ${n} explanation${n === 1 ? '' : 's'}`}
        />
        <div
          className={inside ? 'value inside' : 'value'}
          style={{
            color: inside ? 'var(--ink)' : colour,
            // exactly ONE of left/right may be set -- setting both stretches the
            // element across the bar instead of anchoring it to an end
            ...(good
              ? (inside
                  ? { right: `calc(${50 - pct}% + 8px)`, left: 'auto' }
                  : { left: `calc(${50 + pct}% + 8px)`, right: 'auto' })
              : (inside
                  ? { left: `calc(${50 - pct}% + 8px)`, right: 'auto' }
                  : { right: `calc(${50 + pct}% + 8px)`, left: 'auto' })),
          }}
        >
          {sign}{pctOf(value)}%
        </div>
      </div>

      <div className="pole right">{right}</div>
    </div>
  )
}

function Eyebrow() {
  return <p className="eyebrow">The Optimism Map</p>
}

/** Full-height state screen, vertically centred. */
function State({ children, quiet = false }) {
  return (
    <div className="state">
      <Compass className="state-icon" size={40} weight="thin" aria-hidden="true" />
      <Eyebrow />
      <p className={quiet ? 'state-text quiet' : 'state-text'}>{children}</p>
    </div>
  )
}

/** The rungs a concept can be on, in order, shown as filled pips. */
const RUNGS = ['discriminate', 'detect', 'produce', 'live']

function Focus({ items }) {
  if (!items.length) return null
  return (
    <section className="block focus">
      <h2 className="heading">what you're working on</h2>
      {items.map((c) => {
        const at = RUNGS.indexOf(c.mastery)
        return (
          <div className="focus-row" key={c.id}>
            <span className="focus-name">{c.name}</span>
            <span className="pips" title={c.mastery}>
              {RUNGS.map((r, i) => (
                <i key={r} className={i <= at ? 'pip on' : 'pip'} />
              ))}
            </span>
          </div>
        )
      })}
    </section>
  )
}

export default function App() {
  const [focus, setFocus] = useState([])
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = () => {
      fetch('/api/reading')
        .then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e.detail))))
        .then(setData)
        .catch((e) => setError(String(e)))
      fetch('/api/focus')
        .then((r) => (r.ok ? r.json() : { focus: [] }))
        .then((d) => setFocus(d.focus || []))
        .catch(() => {})
    }
    load()
    // the skill writes from chat while this page sits open, so poll
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  if (error) return <State>{error}</State>
  if (!data) return <State quiet>reading…</State>
  if (!data.n) return <State>Nothing here yet.<br />Bring something to the skill in chat.</State>

  const rd = data.readiness
  if (rd && !rd.ready) {
    return (
      <State>
        Still listening — {rd.total.have} of {rd.total.need}.
        <br />
        <span className="muted">
          {rd.bad.have}/{rd.bad.need} setbacks · {rd.good.have}/{rd.good.need} wins
        </span>
      </State>
    )
  }

  return (
    <div className="page">
      <Eyebrow />
      <h1 className="title">How you explain the things that happen to you.</h1>
      {data.trend !== null && data.trend !== undefined && (
        <p className="trend">
          <span style={{ color: data.trend >= 0 ? 'var(--good)' : 'var(--bad)' }}>
            {data.trend > 0 ? '↑' : data.trend < 0 ? '↓' : '·'}{' '}
            {Math.abs(Math.round((data.trend / 3) * 100))}%
          </span>{' '}
          since the {data.window} before these
        </p>
      )}

      <div className="axis">
        <span className="lo">← pessimistic</span>
        <span className="hi">optimistic →</span>
      </div>

      {data.overall !== null && (
        <div className="overall">
          <Row row={{ left: 'Overall', right: '', value: data.overall, n: data.n }} overall />
        </div>
      )}

      {data.blocks.map((b) => (
        <section className="block" key={b.heading}>
          <h2 className="heading">{b.heading}</h2>
          {b.rows.map((r) => <Row key={r.dim} row={r} />)}
        </section>
      ))}

      <Focus items={focus} />
    </div>
  )
}

