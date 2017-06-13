import Inferno from 'inferno';
import Component from 'inferno-component';

import './ChalModal.scss';

export default class ChalModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      input: '',
      showSolvesView: false
    };

    this.toggleSolvesView = this.toggleSolvesView.bind(this);

    this.onInputKeyDown = this.onInputKeyDown.bind(this);
    this.onInputChange = this.onInputChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.challenge != nextProps.challenge) {
      this.setState(state => {
        state.input = '';
        state.showSolvesView = false;
      });
    }
  }

  toggleSolvesView() {
    this.setState(state => {
      state.showSolvesView = !state.showSolvesView;
    });
  }

  onInputKeyDown(e) {
    if (e.key === 'Enter') {
      this.onSubmit();
    }

    if (e.key === 'Escape') {
      this.setState(state => {
        state.input = '';
      });
    }
  }

  onInputChange(e) {
    this.setState(state => {
      state.input = e.target.value;
    });
  }

  onSubmit() {
    if (!this.state.input.length) return;
    this.props.submit(this.state.input);
  }

  classFromResponse(response) {
    if (!response) {
      return '';
    }

    switch (response.status) {
      case 0:
        return 'error';
      case 1:
        return 'success';
      default:
        return 'info';
    }
  }

  textFromResponse(response) {
    return response ? response.message : '';
  }

  render() {
    const { challenge, solves, hide, submit, response } = this.props;

    if (!challenge) {
      return <div className="chal-modal-container" />;
    }

    return (
      <div className="chal-modal-container open" onClick={hide}>
        <div className="chal-modal">
          {!this.state.showSolvesView &&
            <div className="chal-content">
              {solves &&
                <div className="chal-solves" onClick={this.toggleSolvesView}>
                  {solves.length} Solves
                </div>}
              <div className="chal-row">
                <div className="chal-category">
                  {challenge.category}
                </div>
                <div className="chal-name">
                  {challenge.name}
                </div>
                <div className="chal-desc">
                  {challenge.description}
                </div>
                <div className="chal-files">
                  {challenge.files.map(file =>
                    <a className="chal-file" href={`/files/${file}`} download>{file.split('/').slice(-1)[0]}</a>
                  )}
                </div>
              </div>
              <div className="chal-row">
                <div className="chal-input">
                  <div className="chal-input-row">
                    <input
                      className={'csaw-form-control ' + this.classFromResponse(response)}
                      type="text"
                      placeholder="Key"
                      onKeyDown={this.onInputKeyDown}
                      onInput={this.onInputChange}
                      value={this.state.input}
                    />
                    <button className="btn btn-primary" onClick={this.onSubmit}>Submit</button>
                  </div>
                  <div className="chal-input-row">
                    <div className={'chal-response ' + this.classFromResponse(response)}>
                      {response ? response.message : '\u00A0'}
                    </div>
                  </div>
                </div>
              </div>
            </div>}
          {this.state.showSolvesView &&
            <div className="chal-content chal-solves-container">
              <div className="chal-solves" onClick={this.toggleSolvesView}>
                <i className="fa fa-arrow-left" /><span style={{ marginLeft: '5px' }}>Challenge</span>
              </div>
              <div class="chal-category">Solves</div>
              <div className="solves-table">
                {solves &&
                  solves.map(solve => {
                    return (
                      <div className="chal-solve">
                        <div><a href={'/team/' + solve.id} target="_blank">{solve.name}</a></div>
                        <div className="pull-right">{new Date(solve.date).toLocaleString()}</div>
                      </div>
                    );
                  })}
              </div>
            </div>}
        </div>
      </div>
    );
  }
}
