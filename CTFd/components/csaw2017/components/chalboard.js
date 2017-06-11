import Inferno from 'inferno';
import Component from 'inferno-component';
import axios from 'axios';

import ChalToolbar from './ChalToolbar';
import ChalGrid from './ChalGrid';

import './Chalboard.scss';

class Chalboard extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
      challenges: []
    };

    this.loadChals = this.loadChals.bind(this);
  }

  componentWillMount() {
    this.loadChals();
  }

  async loadChals() {
    const challenges = (await axios.get('/chals')).data.game;

    this.setState(state => {
      state.challenges = challenges;
      state.loading = false;
    });
  }

  render() {
    return (
      <div className="chalboard container">
        <ChalToolbar />
        <ChalGrid challenges={this.state.challenges} loading={this.state.loading} />
      </div>
    );
  }
}

Inferno.render(<Chalboard />, document.getElementById('challenges-container'));
