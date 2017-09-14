import Inferno from 'inferno'
import Component from 'inferno-component'

import './ChalProgress.scss'

export default class ChalProgress extends Component {
  constructor(props) {
    super(props)

    this.state = {
      completed: 0,
      total: 1,
      pct: '0%',
    }

    this.renderBar = this.renderBar.bind(this)
  }

  componentDidMount() {
    this.renderBar()
  }

  componentDidUpdate() {
    if (
      this.state.completed != this.props.completed ||
      this.state.total != this.props.total ||
      this.props.total >= this.props.completed
    ) {
      this.renderBar()
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.completed <= nextProps.total) {
      this.setState(state => {
        state.completed = nextProps.completed
        state.total = nextProps.total
      })
    }
  }

  renderBar() {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        this.setState(state => {
          state.pct = (this.state.completed / this.state.total * 100).toFixed(2) + '%'
        })
      })
    })
  }

  render() {
    const { loading } = this.props

    return (
      <div className={'chal-progress' + (loading ? ' loading' : '')}>
        <span className="progress-pct">{this.state.pct}</span>
        <span className="progress-pts">
          ({this.state.completed} / {this.state.total})
        </span>
        <div className="progress-bar-bg" />
        <div className="progress-bar" style={{ width: this.state.pct }} />
      </div>
    )
  }
}

ChalProgress.defaultProps = {
  loading: true,
  completed: 0,
  total: 100,
}
